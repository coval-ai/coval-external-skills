#!/usr/bin/env python3
"""Send one minimal OTLP JSON span to Coval for trace ingestion checks."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def build_payload(service_name: str) -> dict:
    now_ms = int(time.time() * 1000)
    trace_id = f"{now_ms:032x}"[-32:]
    span_id = f"{now_ms:016x}"[-16:]
    start_ns = now_ms * 1_000_000
    end_ns = start_ns + 1_000_000
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"stringValue": service_name},
                        }
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "coval.external-skills"},
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": span_id,
                                "name": "debug-validation-span",
                                "kind": 1,
                                "startTimeUnixNano": str(start_ns),
                                "endTimeUnixNano": str(end_ns),
                                "attributes": [
                                    {
                                        "key": "coval.validation",
                                        "value": {"boolValue": True},
                                    }
                                ],
                                "status": {"code": 1},
                                "events": [],
                                "links": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send one OTLP JSON span to Coval /v1/traces.",
    )
    parser.add_argument("--api-key", required=True, help="Coval API key")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--simulation-id", help="Simulation output ID")
    target.add_argument("--conversation-id", help="Monitoring conversation ID")
    parser.add_argument(
        "--endpoint",
        default="https://api.coval.dev/v1/traces",
        help="Coval trace endpoint",
    )
    parser.add_argument(
        "--service-name",
        default="coval-external-skills-validation",
        help="service.name resource attribute",
    )
    parser.add_argument(
        "--allow-not-found",
        action="store_true",
        help="Exit 0 on 404. Use only for intentional fake-ID connectivity checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    body = json.dumps(build_payload(args.service_name)).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": args.api_key,
    }
    if args.simulation_id:
        headers["X-Simulation-Id"] = args.simulation_id
    else:
        headers["X-Conversation-Id"] = args.conversation_id

    request = urllib.request.Request(
        args.endpoint,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            print(f"status={response.status}")
            if response_body:
                print(response_body)
            return 0 if response.status == 200 else 1
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        print(f"status={error.code}")
        if response_body:
            print(response_body)
        known_fake_id = args.simulation_id == "wizard-test"
        return 0 if error.code == 404 and (args.allow_not_found or known_fake_id) else 1
    except Exception as error:  # noqa: BLE001
        print(f"error={error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
