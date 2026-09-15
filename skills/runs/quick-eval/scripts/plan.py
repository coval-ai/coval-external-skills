#!/usr/bin/env python3
"""Validate a local explicit-subset run plan. Performs no network calls."""
import argparse
import json
from pathlib import Path


def positive(value, name, maximum=None):
    if type(value) is not int or value < 1 or (maximum and value > maximum):
        raise ValueError(f"{name} must be a positive integer" + (f" <= {maximum}" if maximum else ""))
    return value


def unique_ids(values, name):
    if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError(f"{name} must be an explicit non-empty list of IDs")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicate IDs")
    return values


def plan(body, remaining, max_concurrency):
    positive(remaining, "remaining simulations")
    positive(max_concurrency, "max concurrency", 100)
    if not isinstance(body, dict):
        raise ValueError("launch must be a JSON object")
    for key in ("agent_id", "persona_id", "test_set_id"):
        if not isinstance(body.get(key), str) or not body[key].strip():
            raise ValueError(f"missing {key}")
    options = body.get("options", {})
    if not isinstance(options, dict):
        raise ValueError("options must be an object")
    cases = unique_ids(options.get("test_case_ids"), "options.test_case_ids")
    if len(cases) > 100:
        raise ValueError("at most 100 explicit cases per request")
    if options.get("sub_sample_size", 0) not in (0, None):
        raise ValueError("do not combine explicit cases and random sub-sampling")
    iterations = positive(options.get("iteration_count", 1), "iterations", 50)
    concurrency = positive(options.get("concurrency", 1), "concurrency", 100)
    if concurrency > max_concurrency:
        raise ValueError("concurrency exceeds the authorized limit")
    single, multiple = body.get("mutation_id"), body.get("mutation_ids")
    if single is not None and multiple is not None:
        raise ValueError("mutation_id and mutation_ids are mutually exclusive")
    if single is not None and (not isinstance(single, str) or not single.strip()):
        raise ValueError("mutation_id must be a non-empty ID")
    mutations = unique_ids(multiple, "mutation_ids") if multiple is not None else ([single] if single else [])
    if len(mutations) > 100:
        raise ValueError("at most 100 mutations")
    metrics = unique_ids(body.get("metric_ids"), "metric_ids")
    overrides = body.get("config_overrides")
    if not isinstance(overrides, dict):
        raise ValueError("set a verified config_overrides.simulation_timeout_seconds limit")
    duration = positive(overrides.get("simulation_timeout_seconds"), "simulation_timeout_seconds")
    count = len(cases) * iterations * (1 + len(mutations))
    if count > remaining:
        raise ValueError(f"plan needs {count} simulations; only {remaining} authorized remaining")
    return {
        "simulations": count,
        "variants_including_base": 1 + len(mutations),
        "selected_cases": len(cases),
        "iterations": iterations,
        "concurrency": concurrency,
        "requested_metric_evaluations": count * len(metrics),
        "configured_call_seconds": duration,
        "configured_total_call_minutes_upper_bound": count * duration / 60,
        "remaining_simulations_after_plan": remaining - count,
        "limitation": "Local arithmetic only; not an ownership check, cost quote or server-enforced budget.",
    }


def plan_batch(body, remaining, max_concurrency):
    """Accept one request or a list, reserving the same local budget across personas."""
    if not isinstance(body, list):
        return plan(body, remaining, max_concurrency)
    if not body:
        raise ValueError("batch must contain at least one launch")
    results = []
    for launch in body:
        result = plan(launch, remaining, max_concurrency)
        remaining = result["remaining_simulations_after_plan"]
        results.append(result)
    return {"launches": results, "simulations": sum(r["simulations"] for r in results),
            "requested_metric_evaluations": sum(r["requested_metric_evaluations"] for r in results),
            "configured_total_call_minutes_upper_bound": sum(r["configured_total_call_minutes_upper_bound"] for r in results),
            "remaining_simulations_after_plan": remaining,
            "limitation": "Local batch arithmetic only; does not reserve or enforce budget on the server."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch", type=Path, required=True)
    parser.add_argument("--remaining-simulations", type=int, required=True)
    parser.add_argument("--max-concurrency", type=int, default=1)
    args = parser.parse_args()
    try:
        result = plan_batch(json.loads(args.launch.read_text()), args.remaining_simulations, args.max_concurrency)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Plan rejected: {exc}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
