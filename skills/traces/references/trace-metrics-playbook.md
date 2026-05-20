# Trace Metrics Playbook

Custom trace metrics extract values from OpenTelemetry spans. Create them only when the span and attribute exist in real Coval trace data.

## Supported Aggregations

Numeric attribute aggregations:
- `average`
- `median`
- `p90`
- `p95`
- `p99`
- `max`
- `min`
- `sum`

Span-level aggregations:
- `count`
- `error_rate`
- `success_rate`

The target environment's public API/OpenAPI is authoritative for metric
creation. Some production API deployments accept only `average`, `median`,
`p90`, `max`, and `min`; use one of those numeric aggregations as a fallback and
record the broader desired metric as public API/docs drift.

Units:
- `s`
- `ms`
- `count`
- `ratio`
- `percent`
- `tokens`
- `score`

If the desired display unit is not supported, omit `unit` and include the unit
in the metric name, description, or attribute name.

## Metric Quality Bar

Create metrics that a customer can use to operate the agent, not just prove
that tracing is wired. A useful metric answers one concrete question:
- Is a customer-facing workflow completing?
- Which dependency or tool is blocking the workflow?
- Which latency tail makes calls feel slow or time out?
- How often does the agent fall back, escalate, retry, or hit a guardrail?
- Which cost or usage driver is changing over time?

Diagnostic-only metrics, such as generic call duration, root span count, or a
temporary connectivity probe, are useful during setup but should not be the
final custom metric set unless the customer explicitly asked for them.

Not every useful customer metric needs traces. If the value can be computed
from the transcript, simulation output, or conversation metadata without span
data, prefer a standard Coval metric or evaluation metric. For example, "Turns
Per Call" is usually a transcript/conversation aggregate, not a custom trace
metric. "Cart Total" is a good trace metric when the agent exposes the numeric
cart or order amount as a safe span attribute during checkout.

When the API does not accept span-level `error_rate`, `success_rate`, `count`,
`sum`, `p95`, or `p99`, use real numeric attributes with supported aggregations
instead of watering down the question. A numeric `0`/`1` attribute aggregated by
`average` is a rate. A per-conversation count attribute aggregated by `average`
answers "how many per conversation"; use `max` only when the desired signal is
the worst observed count.

## Baseline Metric Sets

Voice agents:
- P95 LLM TTFB: `llm` / `metrics.ttfb` / `p95` / `s`
- P95 TTS TTFB: `tts` / `metrics.ttfb` / `p95` / `s`
- P95 STT TTFB: `stt` / `metrics.ttfb` / `p95` / `s`
- Total output tokens: `llm` / `gen_ai.usage.output_tokens` / `sum` / `tokens`
- STT provider error rate: `stt.provider.<name>` / `error_rate` / `percent`
- Tool failure rate: `llm_tool_call` / `tool.error` / `average` / `ratio`
- Dependency blocked rate: `conversation` / `workflow.dependency_blocked` / `average` / `ratio`
- Tool latency P90: `llm_tool_call` / `tool.latency_ms` / `p90` / `ms`

WebSocket or realtime agents:
- Realtime response TTFB: `llm` or `realtime` / `metrics.ttfb` / `p95` / `s`
- Stream error rate: `transport` or `realtime` / `error_rate` / `percent`
- Total tokens: `llm` / token attributes / `sum` / `tokens`
- Tool count: `llm_tool_call` / `count` / `count`

Conversation monitoring:
- Tool/API error rate: `llm_tool_call` or custom external API span / `error_rate` / `percent`
- P99 model latency: `llm` / `metrics.ttfb` / `p99` / `s`
- Critical event count: custom span / `count` / `count`
- Fallback rate: provider/fallback span / `count` or `error_rate`

## Customer-Signal Recipes

Use these recipes when the real span data has the attribute, or when you are
adding instrumentation and have a validation run in progress to prove it.

| Customer Question | Metric | Span / Attribute / Aggregation / Unit | Instrumentation Requirement |
|-------------------|--------|----------------------------------------|-----------------------------|
| How often is the workflow blocked by a required dependency? | Dependency Blocked Rate | `conversation` / `workflow.dependency_blocked` / `average` / `ratio` | Set `1` on the root conversation when a required tool, API, or provider prevents completion; otherwise `0`. |
| Which tools are failing or returning unusable results? | Tool Failure Rate | `llm_tool_call` / `tool.error` / `average` / `ratio` | Set span status `ERROR` and numeric `tool.error` `1` on failed tool calls, `0` on successful ones. |
| Are tool-heavy workflows becoming too complex? | Tool Calls Per Conversation | `conversation` / `tool.call.count` / `average` / `count` | Aggregate the number of tool calls onto the root conversation span. |
| Which downstream dependencies are slow? | Tool Latency P90 | `llm_tool_call` / `tool.latency_ms` / `p90` / `ms` | Record duration for each tool or external API call. |
| Is the intended outcome happening? | Workflow Completion Rate | `conversation` / `workflow.completed` / `average` / `ratio` | Set `1` when the booking, reschedule, order, claim, handoff, or other target outcome completes; otherwise `0`. |
| How often does the agent need backup behavior? | Fallback Rate | `conversation` / `workflow.fallback_used` / `average` / `ratio` | Set `1` when fallback, retry exhaustion, escalation, or transfer was needed; otherwise `0`. |
| What is the value of completed carts or orders? | Cart Total Avg | `conversation` / `cart.total_amount` / `average` / unit omitted | Record a numeric amount on the root conversation or checkout span; include currency in the attribute name, metric name, or description when needed. |

## Vertical Templates

Customer support:
- escalation count
- CRM lookup latency
- knowledge retrieval latency
- unresolved intent rate

Scheduling or booking:
- availability lookup latency
- booking confirmation count
- reschedule flow error rate
- handoff count

Healthcare intake:
- identity verification span count
- appointment lookup latency
- lab-result tool error rate
- policy or privacy guardrail blocks

Restaurant orders:
- menu lookup latency
- cart update count
- cart total average
- payment or order submission error rate
- substitution flow count

Debt collection or financial services:
- compliance guardrail block rate
- identity verification count
- payment-plan tool latency
- dispute escalation count

Sales:
- CRM enrichment latency
- qualification step count
- quote tool error rate
- handoff-to-human count

## Creation Checklist

For each metric:
1. Write the customer question the metric answers.
2. Confirm trace data is the right source for that question.
3. Confirm the metric is not merely a proof-of-ingest metric.
4. Confirm the span name exists in Trace Search or a trace dump.
5. Confirm the attribute exists and is numeric for numeric aggregations.
6. Pick the aggregation that matches the question:
   - p95/p99 for tail latency
   - average/median for typical behavior
   - sum for total tokens/cost/count-like values
   - count for occurrence rate
   - error_rate/success_rate for reliability
7. Pick a short Title Case metric name.
8. Create the metric with `METRIC_CUSTOM_TRACE`.
9. Attach it to the agent or run.
10. Run a small evaluation and verify it computes.
11. Record the computed value and the operational interpretation.
12. If the API rejects an aggregation that exists in current code, create a production-safe fallback metric only when it still answers a useful question.

## Example API Payloads

P95 latency:
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

Tool error rate:
```json
{
  "metric_name": "Tool Error Rate",
  "description": "Percentage of tool call spans with ERROR status.",
  "metric_type": "METRIC_CUSTOM_TRACE",
  "span_name": "llm_tool_call",
  "aggregation_method": "error_rate",
  "unit": "percent"
}
```

Production-safe tool failure rate:
```json
{
  "metric_name": "Tool Failure Rate",
  "description": "Share of tool call spans where the tool returned an error or unusable response.",
  "metric_type": "METRIC_CUSTOM_TRACE",
  "span_name": "llm_tool_call",
  "metric_attribute": "tool.error",
  "aggregation_method": "average",
  "unit": "ratio"
}
```

Dependency blocked rate:
```json
{
  "metric_name": "Dependency Blocked Rate",
  "description": "Share of conversations where a required dependency prevented the target workflow from completing.",
  "metric_type": "METRIC_CUSTOM_TRACE",
  "span_name": "conversation",
  "metric_attribute": "workflow.dependency_blocked",
  "aggregation_method": "average",
  "unit": "ratio"
}
```

Cart total average:
```json
{
  "metric_name": "Cart Total Avg",
  "description": "Average numeric cart amount captured by the agent during checkout.",
  "metric_type": "METRIC_CUSTOM_TRACE",
  "span_name": "conversation",
  "metric_attribute": "cart.total_amount",
  "aggregation_method": "average"
}
```
