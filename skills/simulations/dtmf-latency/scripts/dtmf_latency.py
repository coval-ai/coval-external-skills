#!/usr/bin/env python3
"""Compute DTMF-keypress-to-first-response latency from Coval simulation JSON.

Usage:
    python3 dtmf_latency.py sim1.json [sim2.json ...] [--digits 1]
        [--timeout-threshold 15] [--debug]

Each input file is the JSON returned by `coval simulations get <id> --format json`
or `GET https://api.coval.dev/v1/simulations/{id}` (both shapes handled).

Prints a JSON report to stdout. All arithmetic happens here — the calling agent
must render this output verbatim and never recompute values.

Event statuses:
    OK            keypress followed by an assistant response; latency computed
    TIMEOUT       no assistant speech after the keypress; latency is a lower bound
    NO_TIMESTAMPS keypress or response turn lacks usable timestamps

Each event also carries user_spoke_first: true when the simulated caller spoke
again before the bot responded to the keypress — the measured latency then spans
that user turn, and usually means the bot never acknowledged the DTMF itself.

Simulation statuses:
    OK             at least one DTMF event found
    NO_DTMF        transcript present but no DTMF tool-call turns
    NOT_ANALYZABLE no transcript (failed / empty simulation)
"""

import argparse
import json
import statistics
import sys


def load_simulation(path):
    with open(path) as f:
        data = json.load(f)
    sim = data.get("simulation", data)
    transcript = sim.get("transcript")
    if isinstance(transcript, str):
        try:
            transcript = json.loads(transcript)
        except (ValueError, TypeError):
            transcript = None
    return sim, transcript if isinstance(transcript, list) else None


def ftime(turn, key):
    val = turn.get(key)
    try:
        val = float(val)
    except (TypeError, ValueError):
        return None
    return val if val > 0 else None


def is_dtmf_turn(turn):
    return (
        bool(turn.get("is_tool_call"))
        and "dtmf" in str(turn.get("name") or "").lower()
        and turn.get("tool_call_owner") == "user"
    )


def dtmf_digits(turn):
    content = turn.get("content")
    if isinstance(content, str):
        try:
            args = json.loads(content).get("arguments", {})
            if args.get("digits"):
                return str(args["digits"])
        except (ValueError, AttributeError):
            pass
    return "?"


def extract_events(transcript):
    """Group DTMF turns into events (bursts collapse into one) and find responses."""
    events = []
    for i, turn in enumerate(transcript):
        if not is_dtmf_turn(turn):
            continue
        anchor = ftime(turn, "end_time") or ftime(turn, "start_time")
        if events:
            prev = events[-1]
            answered = any(
                t.get("role") == "assistant" and not t.get("is_tool_call")
                for t in transcript[prev["_last_idx"] + 1 : i]
            )
            if not answered:  # burst: same event, no bot speech in between
                prev["digits"] += dtmf_digits(turn)
                prev["press_count"] += 1
                if anchor:
                    prev["pressed_end"] = anchor
                prev["_last_idx"] = i
                continue
        events.append({
            "digits": dtmf_digits(turn),
            "press_count": 1,
            "pressed_end": anchor,
            "_last_idx": i,
        })

    for ev in events:
        response = None
        user_spoke_first = False
        for t in transcript[ev["_last_idx"] + 1:]:
            if t.get("is_tool_call"):
                continue
            if (
                t.get("role") == "assistant"
                and (ftime(t, "start_time") or 0) >= (ev["pressed_end"] or 0)
            ):
                response = t
                break
            if t.get("role") == "user":
                user_spoke_first = True
        ev["user_spoke_first"] = user_spoke_first
        if ev["pressed_end"] is None:
            ev["status"] = "NO_TIMESTAMPS"
            ev["response_start"] = None
            ev["latency"] = None
        elif response is None:
            last_end = max(
                (ftime(t, "end_time") or 0 for t in transcript), default=0
            )
            ev["status"] = "TIMEOUT"
            ev["response_start"] = None
            ev["latency"] = None
            ev["latency_lower_bound"] = round(max(last_end - ev["pressed_end"], 0), 2)
        else:
            start = ftime(response, "start_time")
            if start is None:
                ev["status"] = "NO_TIMESTAMPS"
                ev["response_start"] = None
                ev["latency"] = None
            else:
                ev["status"] = "OK"
                ev["response_start"] = round(start, 2)
                ev["latency"] = round(start - ev["pressed_end"], 2)
        if ev["pressed_end"] is not None:
            ev["pressed_end"] = round(ev["pressed_end"], 2)
        del ev["_last_idx"]
    return events


def percentile(values, pct):
    if not values:
        return None
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    k = (len(vals) - 1) * pct / 100.0
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return round(vals[lo] + (vals[hi] - vals[lo]) * (k - lo), 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--digits", help="only include events whose digits match exactly")
    parser.add_argument(
        "--timeout-threshold", type=float, default=15.0,
        help="latencies at or above this are always flagged as outliers (seconds)",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="also list every tool-call turn name seen, per simulation",
    )
    args = parser.parse_args()

    sims_out = []
    for path in args.files:
        try:
            sim, transcript = load_simulation(path)
        except (OSError, ValueError) as exc:
            print(f"warning: skipping {path}: {exc}", file=sys.stderr)
            continue
        entry = {
            "simulation_id": sim.get("simulation_id"),
            "test_case_id": sim.get("test_case_id"),
            "run_id": sim.get("run_id"),
        }
        if transcript is None:
            entry["status"] = "NOT_ANALYZABLE"
            entry["events"] = []
        else:
            events = extract_events(transcript)
            if args.digits:
                events = [e for e in events if e["digits"] == args.digits]
            entry["status"] = "OK" if events else "NO_DTMF"
            entry["events"] = events
            if args.debug:
                entry["debug_tool_call_names"] = sorted(
                    {str(t.get("name")) for t in transcript if t.get("is_tool_call")}
                )
        sims_out.append(entry)

    all_events = [
        dict(ev, simulation_id=s["simulation_id"], run_id=s.get("run_id"))
        for s in sims_out for ev in s["events"]
    ]
    latencies = [e["latency"] for e in all_events if e["status"] == "OK"]
    timeouts = [e for e in all_events if e["status"] == "TIMEOUT"]

    median = statistics.median(latencies) if latencies else None
    outlier_cutoff = max(2 * median, 6.0) if median is not None else None
    outliers = timeouts + [
        e for e in all_events
        if e["status"] == "OK"
        and (e["latency"] > outlier_cutoff or e["latency"] >= args.timeout_threshold)
    ]

    def latency_stats(evs):
        ok = [e for e in evs if e["status"] == "OK"]
        acked = [e for e in ok if not e.get("user_spoke_first")]
        values = [e["latency"] for e in ok]
        n_timeouts = sum(1 for e in evs if e["status"] == "TIMEOUT")
        return {
            "events_measured": len(values),
            "timeouts": n_timeouts,
            "average": round(statistics.mean(values), 2) if values else None,
            "median": round(statistics.median(values), 2) if values else None,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "p95": percentile(values, 95),
            "buckets": {
                "acknowledged_lt_1s": sum(1 for e in acked if e["latency"] < 1),
                "acknowledged_1_to_4s": sum(1 for e in acked if 1 <= e["latency"] <= 4),
                "acknowledged_gt_4s": sum(1 for e in acked if e["latency"] > 4),
                "never_acknowledged_caller_spoke_first": len(ok) - len(acked),
                "timeout_no_response": n_timeouts,
            },
        }

    by_run = {}
    for run_id in {e["run_id"] for e in all_events}:
        by_run[str(run_id)] = latency_stats(
            [e for e in all_events if e["run_id"] == run_id]
        )

    report = {
        "simulations": sims_out,
        "aggregate": {
            **latency_stats(all_events),
            "events_no_timestamps": sum(
                1 for e in all_events if e["status"] == "NO_TIMESTAMPS"
            ),
            "simulations_analyzed": sum(1 for s in sims_out if s["status"] == "OK"),
            "simulations_no_dtmf": sum(1 for s in sims_out if s["status"] == "NO_DTMF"),
            "simulations_not_analyzable": sum(
                1 for s in sims_out if s["status"] == "NOT_ANALYZABLE"
            ),
            "outlier_cutoff": round(outlier_cutoff, 2) if outlier_cutoff else None,
        },
        "by_run": by_run,
        "outliers": outliers,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
