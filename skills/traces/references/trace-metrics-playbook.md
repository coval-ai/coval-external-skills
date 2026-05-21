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
- Workflow completion rate: `conversation` / `workflow.completed` / `average` / `ratio`
- Fallback used rate: `conversation` / `workflow.fallback_used` / `average` / `ratio`
- One vertical-specific failure-mode metric, such as
  `conversation` / `roadside.dispatch.latency_ms` / `p90` / `ms`

Only create LLM/TTS/STT latency metrics when those spans contain measured
provider timing. For Vapi artifact-derived marker spans, use tool/workflow
metrics and trace-aware judges instead.

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
| Is the known business-critical dependency causing the demo/customer failure mode? | Vertical Dependency Latency P90 | `conversation` / `<domain>.<dependency>.latency_ms` / `p90` / `ms` | Copy the latency from the specific tool/workflow span onto the root or a canonical span with a low-cardinality attribute, e.g. `roadside.dispatch.latency_ms`. |

## First-Pass Metric Floor

When the trace already emits tool and root workflow attributes, do not stop at
three or four proof metrics. Create or stage this minimum set before handoff:

1. One vertical-specific metric for the customer's most important failure mode.
2. Workflow Completion Rate.
3. Workflow Blocked Rate or Dependency Blocked Rate.
4. Tool Latency P90.
5. Tool Failure Rate.
6. Fallback Used Rate when fallback/retry/escalation is visible.
7. Tool Calls Per Conversation when tool complexity is part of the workflow.

If any item cannot be created, say why in concrete terms: missing span,
missing numeric attribute, stub-only tool handler, rejected API field, or no
representative run yet. Do not replace a missing vertical metric with a generic
span-count metric.

## Trace-Aware LLM Judge Recipes

LLM judge metrics with `include_traces: true` are useful when the judge needs
both transcript and trace context. They complement `METRIC_CUSTOM_TRACE`; they
do not replace numeric trace metrics.

Use them for questions like:
- Did the agent verify identity before account-specific tool calls?
- Did spoken claims match successful tool outputs?
- Did the agent recover correctly after tool errors or dependency failures?
- Did the agent confirm sensitive identifiers before using them in tool
  arguments?

Creation rules:
1. Fetch the current Metrics OpenAPI and verify `include_traces` is supported
   for the selected LLM judge metric type.
2. Reuse the customer's existing judge intent, but create a new trace-aware
   version unless the customer explicitly asked to mutate the existing metric.
3. In the prompt, name the trace evidence the judge should use:
   `llm_tool_call`, `function.name`, `function.arguments`, `tool.error`,
   `error.type`, and root workflow attributes.
4. Attach the judge to the same agent/run template as the numeric trace metrics.
5. Run a validation simulation and report the computed value.

Example:
```json
{
  "metric_name": "Trace-Aware Tool Output Grounding",
  "description": "Uses transcript plus OTel tool-call traces to verify agent claims are grounded in successful tool outputs.",
  "metric_type": "METRIC_LLM_BINARY",
  "prompt": "Use BOTH the transcript and OTel trace context. Score YES only if the agent's customer-facing claims are supported by successful llm_tool_call outputs. Score NO if the agent asserts outcomes not supported by successful tool outputs, or if it ignores a tool.error or error.type result and presents the workflow as completed.",
  "include_traces": true
}
```

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

Insurance:
- roadside dispatch latency P90
- FNOL field capture count
- fraud pattern detected rate
- roadside dependency blocked rate
- callback or fallback offered rate

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
