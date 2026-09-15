#!/usr/bin/env python3
"""Read a bounded, paginated Coval run evidence snapshot. No mutations or retries."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request


BASE = "https://api.coval.dev/v1"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("API redirect refused; verify the documented endpoint")


def get_client(key, workspace):
    opener = urllib.request.build_opener(NoRedirect)

    def get(path, params=None):
        url = BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"x-api-key": key, "Accept": "application/json", "X-Coval-Workspace-Id": workspace}
        request = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(request, timeout=45) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            raise ValueError(f"GET {path} returned HTTP {exc.code}; no complete snapshot written") from None
        except urllib.error.URLError:
            raise ValueError(f"GET {path} could not connect; no complete snapshot written") from None
        if not isinstance(data, dict):
            raise ValueError(f"GET {path} returned a non-object payload")
        return data

    return get


def pages(get, path, key, params, limit):
    rows, tokens = [], set()
    query = {**params, "page_size": min(100, limit)}
    while True:
        data = get(path, query)
        batch = data.get(key)
        if not isinstance(batch, list) or any(not isinstance(item, dict) for item in batch):
            raise ValueError(f"GET {path} missing expected {key} array")
        rows.extend(batch)
        if len(rows) > limit:
            raise ValueError(f"GET {path} exceeds the {limit}-row evidence budget")
        token = data.get("next_page_token")
        if not token:
            return rows
        if not isinstance(token, str) or token in tokens:
            raise ValueError(f"GET {path} returned an invalid/repeated pagination token")
        if len(rows) >= limit or len(tokens) >= limit:
            raise ValueError(f"GET {path} has more pages than the evidence budget allows")
        tokens.add(token)
        query["page_token"] = token


def resource(data, key):
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"missing {key} resource envelope")
    return value


def selected(value, keys):
    return {key: value[key] for key in keys if key in value}


def snapshot(get, run_id, workspace, limit):
    run = resource(get(f"/runs/{run_id}"), "run")
    if run.get("run_id") != run_id:
        raise ValueError("run ID mismatch")
    listings = pages(get, "/conversations/simulated", "simulated_conversations", {"filter": f'run_id="{run_id}"'}, limit)
    records, seen = [], set()
    for item in listings:
        sim_id = item.get("simulation_id")
        if not isinstance(sim_id, str) or not re.fullmatch(r"[A-Za-z0-9]{22}", sim_id):
            raise ValueError("missing/invalid simulation ID")
        if sim_id in seen or item.get("run_id") != run_id:
            raise ValueError("duplicate or out-of-run simulation in scoped response")
        seen.add(sim_id)
        detail = resource(get(f"/conversations/simulated/{sim_id}"), "simulated_conversation")
        if detail.get("simulation_id") != sim_id or detail.get("run_id") != run_id:
            raise ValueError("simulation detail identity/run mismatch")
        metrics = pages(get, f"/conversations/simulated/{sim_id}/metrics", "metrics",
                        {"include_superseded": "true"}, 500)
        metric_ids = [m.get("metric_output_id") for m in metrics]
        if any(not v for v in metric_ids) or len(set(metric_ids)) != len(metric_ids):
            raise ValueError("missing/duplicate metric output IDs")
        record = selected(detail, ["simulation_id", "run_id", "status", "test_case_id", "agent_id", "persona_id",
                                   "test_set_id", "mutation_id", "has_audio", "transcript", "create_time",
                                   "error_message", "error_status", "end_reason"])
        record["metrics"] = [selected(m, ["metric_output_id", "metric_id", "metric_version_ulid", "status",
                                          "status_reason", "value", "explanation", "create_time", "start_time",
                                          "end_time", "subvalues_by_timestamp", "subvalues_by_timestamp_truncated"])
                              for m in metrics]
        records.append(record)
    return {
        "schema_version": 1,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "api_url": BASE,
        "workspace_id": workspace,
        "run": selected(run, ["run_id", "display_name", "status", "create_time", "update_time", "agent_id",
                              "persona_id", "test_set_id", "progress", "results", "error", "error_status"]),
        "simulations": records,
        "audit": {
            "observed_simulations": len(records),
            "simulation_statuses": dict(Counter(r.get("status", "UNKNOWN") for r in records)),
            "metric_statuses": dict(Counter(m.get("status", "UNKNOWN") for r in records for m in r["metrics"])),
            "audio_available_count": sum(r.get("has_audio") is True for r in records),
            "transcript_present_count": sum(bool(r.get("transcript")) for r in records),
            "pagination_complete_at_fetch": True,
            "limitations": ["Run may still change; compare observed rows to the saved launch plan.",
                            "Audio availability is not listening proof; no automatic quality judgment.",
                            "All metric output history is included; select exact output IDs/versions, not every row as a new test.",
                            "Bounded criterion subvalues may be incomplete; inspect the exact full metric output when flagged.",
                            "API key/tenant identity must be established separately from the workspace label.",
                            "Sensitive transcripts may be present. Review and redact before sharing."],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--max-conversations", type=int, default=100)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9]{22}", args.run_id):
        parser.error("run ID must be a returned 22-character Coval ID")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.workspace_id):
        parser.error("invalid workspace ID")
    if not 1 <= args.max_conversations <= 1000:
        parser.error("max-conversations must be between 1 and 1000")
    key = os.environ.get("COVAL_API_KEY", "").strip()
    if not key:
        parser.error("COVAL_API_KEY must be supplied through the environment")
    if args.out.exists():
        parser.error("output already exists; choose a new evidence snapshot filename")
    try:
        data = snapshot(get_client(key, args.workspace_id), args.run_id, args.workspace_id, args.max_conversations)
        encoded = json.dumps(data, indent=2, allow_nan=False)
        fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(encoded + "\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Evidence fetch failed: {exc}\n")
    print(json.dumps(data["audit"], indent=2))


if __name__ == "__main__":
    main()
