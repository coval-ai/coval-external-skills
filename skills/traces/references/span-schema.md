# Coval Span Schema

Use stable, Coval-recognized span names so the trace viewer, Trace Search,
built-in trace metrics, and custom trace metrics work well. This mirrors the
public Span Naming Conventions in the Coval OpenTelemetry docs.

## Canonical Spans

| Span | Use For | Required Attributes | Optional / Recommended Attributes | Compatibility Aliases |
|------|---------|---------------------|-----------------------------------|-----------------------|
| `llm` | LLM invocations | - | `metrics.ttfb`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `llm.finish_reason` | - |
| `tts` | Text-to-speech | - | `metrics.ttfb` | - |
| `stt` | Speech-to-text | `transcript` when using STT Word Error Rate or the Audio Upload variant | `metrics.ttfb`, `stt.confidence` | `stt.transcription` for older integrations |
| `stt.provider.<name>` | Per-provider STT attempt, child of `stt` | - | `stt.providerName`, `stt.confidence`, `metrics.ttfb` | - |
| `vad` | Voice activity detection | - | - | - |
| `llm_tool_call` | Individual tool/function calls | - | `function.name`, `tool_call_id`, `function.arguments` | Span name `tool_call`; attributes `tool.name`, `tool.call_id`, `tool.arguments` |
| `turn` | A single conversation turn | - | - | - |
| `conversation` | Full conversation | - | - | - |
| `pipeline` | Processing pipeline | - | - | - |
| `transport` | Audio/network transport | - | - | - |

Any span name works and appears in Coval, but names outside this table get
auto-assigned colors instead of semantic labels. Use `service.name` in the
resource to group spans by service.

New integrations should emit canonical names and attributes first. Add custom
metric attributes to those spans where possible instead of inventing dynamic
span names.

## Metric-Ready Extensions

Use these additive attributes when the agent exposes the data. They are not
required for semantic UI colors, but they make custom trace metrics more useful.

`conversation`:
- `call.duration_seconds`
- safe `session.id`
- safe `customer.workflow`
- `tool.call.count`
- `tool.failure.count`
- `workflow.completed`
- `workflow.dependency_blocked`
- `workflow.fallback_used`
- `cart.total_amount` or `order.total_amount`

`llm_tool_call`:
- `tool.latency_ms`
- `tool.error`
- `tool.dependency_unavailable`
- `tool.result.count`

Use numeric `0`/`1` values for rate-style flags.

## Required For Built-In Value

- STT WER and audio-upload STT WER need an `stt` span with `transcript`.
- LLM/TTS/STT TTFB metrics need `metrics.ttfb` on `llm`, `tts`, or `stt`.
- Token usage needs `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens` on `llm`.
- Tool call analysis needs `llm_tool_call` with `function.name`.
- Custom trace metrics need stable span names and numeric attributes for numeric aggregations.
- Rate-style custom trace metrics should use numeric `0`/`1` attributes when
  the target API requires a `metric_attribute`.

## Status And Errors

Set the span status to `ERROR` for failed tool calls, provider attempts, API calls, timeouts, and guardrail failures. Put a bounded message in the status description or safe attributes such as:
- `error.type`
- `error.message`
- `http.status_code`
- `retry_count`
- `fallback.reason`

Do not encode failures only in span names. Coval custom trace metrics can calculate `error_rate` and `success_rate` from status.

When the deployed metric API requires numeric attributes for rates, also set a
matching `0`/`1` attribute such as `tool.error`,
`tool.dependency_unavailable`, `workflow.dependency_blocked`,
`workflow.completed`, or `workflow.fallback_used`.

## Good Custom Attributes

Choose attributes that answer a debugging or measurement question:
- `retrieval_latency_ms`
- `external_api_latency_ms`
- `queue_wait_ms`
- `handoff_count`
- `retry_count`
- `confidence_score`
- `tool.result.success`
- `tool.result.count`
- `tool.error`
- `tool.latency_ms`
- `tool.dependency_unavailable`
- `tool.call.count`
- `tool.failure.count`
- `workflow.completed`
- `workflow.dependency_blocked`
- `workflow.fallback_used`
- `cart.total_amount`
- `order.total_amount`
- `fallback.used`
- `policy.blocked`
- `appointment.lookup_latency_ms`

Use numeric values for metrics. Keep units clear in the key or metric unit.

## Anti-Patterns

Avoid:
- secrets, tokens, passwords, cookies, or credentials
- raw audio bytes or base64 payloads
- unbounded full prompts/responses
- high-cardinality span names such as `tool_call_<uuid>`
- timestamps as attributes when span timing already captures time
- duplicate manual spans when framework spans already exist and can be enriched
- resending successful batches

Prefer bounded summaries:
- message counts instead of full prompts
- result counts instead of full search results
- redacted or hashed customer identifiers
- low-cardinality workflow labels
