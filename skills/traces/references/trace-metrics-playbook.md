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

## Baseline Metric Sets

Voice agents:
- P95 LLM TTFB: `llm` / `metrics.ttfb` / `p95` / `s`
- P95 TTS TTFB: `tts` / `metrics.ttfb` / `p95` / `s`
- P95 STT TTFB: `stt` / `metrics.ttfb` / `p95` / `s`
- Total output tokens: `llm` / `gen_ai.usage.output_tokens` / `sum` / `tokens`
- STT provider error rate: `stt.provider.<name>` / `error_rate` / `percent`

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
1. Confirm the span name exists in Trace Search or a trace dump.
2. Confirm the attribute exists and is numeric for numeric aggregations.
3. Pick the aggregation that matches the question:
   - p95/p99 for tail latency
   - average/median for typical behavior
   - sum for total tokens/cost/count-like values
   - count for occurrence rate
   - error_rate/success_rate for reliability
4. Pick a short Title Case metric name.
5. Create the metric with `METRIC_CUSTOM_TRACE`.
6. Attach it to the agent or run.
7. Run a small evaluation and verify it computes.
8. If the API rejects an aggregation that exists in current code, create a production-safe fallback metric only when it still answers a useful question.

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
