---
name: configure-trace-metrics
description: Recommend, create, preview, and attach Coval custom trace metrics from OpenTelemetry spans. Use when a user has Coval traces and wants metrics for latency, token usage, provider failures, tool behavior, vertical-specific workflow signals, or production monitoring based on trace attributes.
---

# Configure Coval Trace Metrics

Create metrics from trace data only after at least one real trace exists for the target agent. If traces are absent or sparse, run `setup-tracing` or `optimize-trace-observability` first.

## Read First

Load:
- `../references/trace-metrics-playbook.md`
- `../references/span-schema.md`
- `../references/coval-tracing-reference.md`

## Phase 0: Inventory

Check auth and current resources:
```bash
coval whoami
coval agents list --format json
coval metrics list --include-builtin --format json
```

If the CLI cannot create the required metric shape, use the API after fetching the latest OpenAPI:
```bash
curl -fsS https://api.coval.dev/v1/openapi
```

Collect:
- agent ID and type
- recent run or conversation with traces
- available span names and attributes from Trace Search suggestions, the trace viewer, or a copied trace dump
- existing built-in trace metrics already attached
- customer use case or vertical

## Phase 1: Decide Metric Candidates

Use the playbook to propose a small set. Prefer 3-6 high-signal metrics over a large noisy bundle.

Baseline recommendations:
- voice agents: LLM/TTS/STT TTFB, token usage, tool call count, STT WER when `stt` spans include `transcript`
- realtime or WebSocket agents: model/realtime latency, response TTFB, token usage, stream/error spans
- conversation monitoring: p95/p99 latency, tool/API error rate, count of critical events, production fallback rate
- custom business logic: one metric for the most important customer-specific workflow bottleneck or failure mode

Do not create a custom trace metric for an attribute that is not present in actual trace data unless you are also adding that instrumentation.

## Phase 2: Validate Config Shape

Coval custom trace metric fields:
- `metric_type`: `METRIC_CUSTOM_TRACE`
- `span_name`: exact emitted span name
- `metric_attribute`: required for numeric aggregations
- `aggregation_method`: one of `average`, `median`, `p90`, `p95`, `p99`, `max`, `min`, `sum`, `count`, `error_rate`, `success_rate`
- `unit`: optional display unit such as `s`, `ms`, `count`, `percent`, `tokens`, `ratio`, or `score`

For `count`, `error_rate`, and `success_rate`, omit `metric_attribute` unless the current API explicitly requires it. These are span-level aggregations.

Example API body:
```json
{
  "metric_name": "P95 LLM TTFB",
  "description": "95th percentile time to first token from llm spans.",
  "metric_type": "METRIC_CUSTOM_TRACE",
  "span_name": "llm",
  "metric_attribute": "metrics.ttfb",
  "aggregation_method": "p95",
  "unit": "s"
}
```

Create only after confirming the span/attribute exists in real traces.

## Phase 3: Attach And Verify

After creating metrics:
1. Attach them to the target agent or run configuration using the CLI/API path that matches the current OpenAPI.
2. Launch or rerun one small evaluation.
3. Confirm the metric computes and does not error with "No spans named..." or "metric_attribute is required".
4. If a metric errors because data is missing, fix the instrumentation rather than changing the metric to measure a less useful signal.

## Phase 4: Handoff

Report:
- created metric IDs and names
- span/attribute/aggregation/unit for each
- evidence that each span/attribute existed before creation
- run or conversation used to validate computation
- any recommended follow-up instrumentation
