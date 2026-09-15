#!/usr/bin/env python3
"""Calculate binary calibration from a provenance-bearing local JSON export."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path


def label(value):
    if type(value) in (int, float) and value in (0, 1):
        return int(value)
    if isinstance(value, str) and value.upper() in ("PASS", "FAIL"):
        return int(value.upper() == "PASS")
    raise ValueError("labels must be 0/1 or PASS/FAIL, without implicit thresholding")


def interval(successes, total):
    if not total:
        return {"numerator": successes, "denominator": 0, "rate": None, "wilson_95": None}
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return {"numerator": successes, "denominator": total, "rate": p,
            "wilson_95": [max(0, center - half), min(1, center + half)]}


def calculate(data, split):
    if not isinstance(data, dict) or split not in ("dev", "test"):
        raise ValueError("expected an object and dev or test split")
    for name in ("metric_id", "metric_version", "rubric_id"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"missing {name}")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be an array")
    seen, groups, valid_groups = set(), {}, []
    counts, excluded = Counter({"tp": 0, "tn": 0, "fp": 0, "fn": 0}), Counter()
    considered = 0
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("each record must be an object")
        for name in ("conversation_id", "group_id", "annotation_id", "reviewer"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                raise ValueError(f"missing record {name}")
        if row.get("label_source") != "human":
            raise ValueError("only independently sourced human labels qualify")
        if row.get("split") not in ("train", "dev", "test"):
            raise ValueError("every row must have a train/dev/test split")
        if row["conversation_id"] in seen:
            raise ValueError("duplicate conversation; adjudicate reviewer rows before calibration")
        seen.add(row["conversation_id"])
        previous = groups.setdefault(row["group_id"], row["split"])
        if previous != row["split"]:
            raise ValueError("group leakage across train/dev/test splits")
        if row.get("metric_id") != data["metric_id"] or row.get("metric_version") != data["metric_version"]:
            raise ValueError("mixed or missing metric/version identity")
        if row["split"] != split:
            continue
        considered += 1
        if row.get("review_status") != "COMPLETED":
            excluded["human_review_not_completed"] += 1
            continue
        if row.get("human_label") is None:
            excluded["human_label_missing"] += 1
            continue
        if row.get("metric_status") != "COMPLETED":
            excluded["metric_not_completed"] += 1
            continue
        if row.get("judge_label") is None:
            excluded["judge_label_missing"] += 1
            continue
        human, judge = label(row["human_label"]), label(row["judge_label"])
        counts[{(1, 1): "tp", (1, 0): "fn", (0, 0): "tn", (0, 1): "fp"}[(human, judge)]] += 1
        valid_groups.append(row["group_id"])
    total = sum(counts.values())
    passes, failures = counts["tp"] + counts["fn"], counts["tn"] + counts["fp"]
    warnings = ["Label provenance is asserted by the input; verify original human annotations.",
                "No automatic trust threshold; choose acceptable errors for the product decision."]
    if len(set(valid_groups)) < len(valid_groups):
        warnings.append("Repeated groups: per-call binomial intervals do not establish independent confidence.")
    if not passes or not failures:
        warnings.append("Both human classes are needed; at least one class-specific rate is unknown.")
    if excluded:
        warnings.append("Unscored or unreviewed rows are excluded; inspect selection bias before interpreting rates.")
    return {
        "metric_id": data["metric_id"], "metric_version": data["metric_version"], "rubric_id": data["rubric_id"],
        "split": split,
        "evidence": "insufficient_evidence" if not passes or not failures else
                    ("development_measurement" if split == "dev" else "held_out_measurement_if_untouched"),
        "considered": considered, "scored": total, "independent_groups": len(set(valid_groups)),
        "excluded": dict(excluded), "confusion": dict(counts),
        "pass_recall_tpr": interval(counts["tp"], passes),
        "failure_detection_tnr": interval(counts["tn"], failures),
        "false_pass_rate": interval(counts["fp"], failures),
        "agreement": interval(counts["tp"] + counts["tn"], total), "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--split", choices=["dev", "test"], required=True)
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text()), args.split)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Calibration rejected: {exc}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
