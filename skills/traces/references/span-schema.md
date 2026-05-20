# Coval Span Schema

Use stable, Coval-recognized span names so the trace viewer, Trace Search, built-in trace metrics, and custom trace metrics work well.

## Canonical Spans

| Span | Use | Recommended Attributes |
|------|-----|------------------------|
| `conversation` | Full call/session root | `call.duration_seconds`, safe `session.id`, safe `customer.workflow`, `tool.call.count`, `tool.failure.count`, `workflow.completed`, `workflow.dependency_blocked`, `workflow.fallback_used` |
| `turn` | One user/assistant turn | turn index, safe turn classification |
| `stt` | Final speech-to-text result | `transcript`, `metrics.ttfb`, `stt.confidence` |
| `stt.provider.<name>` | STT provider attempt or fallback | `stt.providerName`, `metrics.ttfb`, `stt.confidence` |
| `llm` | Model invocation | `metrics.ttfb`, `llm.finish_reason`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| `tts` | Text-to-speech invocation | `metrics.ttfb`, provider and voice metadata when safe |
| `llm_tool_call` | Function/tool execution | `function.name`, `tool_call_id`, `function.arguments` when safe, `tool.latency_ms`, `tool.error`, `tool.dependency_unavailable`, `tool.result.count` |
| `vad` | Voice activity detection | confidence, segment duration, state when useful |
| `pipeline` | Agent pipeline wrapper | framework or stage metadata |
| `transport` | Audio/network transport | provider, codec, connection mode, network errors |

Aliases accepted for compatibility:
- `stt.transcription` for `transcript`
- `tool_call` for `llm_tool_call`
- `tool.name` for `function.name`
- `tool.call_id` for `tool_call_id`
- `tool.arguments` for `function.arguments`

New integrations should emit canonical names.

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
