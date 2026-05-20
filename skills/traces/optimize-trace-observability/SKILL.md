---
name: optimize-trace-observability
description: Improve Coval trace quality after basic ingestion works. Use when traces are sparse, missing useful STT/LLM/TTS/tool spans, missing attributes needed for Coval built-in metrics, or when a customer wants maximum debugging and observability value from agent traces.
---

# Optimize Coval Trace Observability

Turn a working but thin Coval trace into a useful debugging artifact. Prefer to
inspect a proven Coval trace first. If `setup-tracing` has launched an initial
asynchronous validation run that is still pending, use the waiting time to make
safe code-visible enrichment, then re-check the finished run before declaring
the optimization complete.

## Read First

Load these references as needed:
- `../references/span-schema.md` for canonical spans, attributes, aliases, and guardrails
- `../references/agent-type-routing.md` for framework-specific trace boundaries
- `../references/coval-tracing-reference.md` for viewer/search behavior and ingestion limits

## Phase 1: Inspect Current Trace Quality

Start from evidence, not assumptions.

1. Find one recent traced simulation or conversation in Coval. Use the Coval
   CLI/API or Trace Search instead of asking the user for a screenshot when
   credentials are available.
2. If the only candidate is an in-flight validation run from `setup-tracing`,
   start or continue a bounded CLI/API poll loop and do not block idly. While
   waiting, inspect the code path and add only enrichment that is clearly safe
   from the implementation.
3. Inspect the trace viewer or exported trace dump once trace data exists.
4. Classify the current trace:
   - no trace
   - trace exists but only root/provider spans
   - STT/LLM/TTS spans exist but lack attributes
   - tool spans missing
   - parent/child structure is flat or misleading
   - attributes are unsafe, oversized, or high-cardinality
5. Check whether existing framework instrumentation should be enriched instead of duplicated.

Do not add manual duplicate spans for operations already emitted by Pipecat, LiveKit, Vapi, or an existing OTel integration unless the existing span cannot be enriched.

## Phase 2: Add Coval-Native Span Coverage

Prioritize spans that make Coval trace UI, built-in trace metrics, and custom trace metrics more useful:
- `conversation`: full call/session root
- `turn`: one user/assistant exchange when the framework exposes a turn boundary
- `stt`: final speech recognition result
- `stt.provider.<name>`: each STT provider attempt or fallback
- `llm`: model call
- `tts`: synthesis call
- `llm_tool_call`: tool/function execution
- `vad`: speech activity decisions when relevant
- `pipeline` or `transport`: only when they help diagnose routing/audio issues

Keep span names stable and low-cardinality. Put IDs, provider names, endpoint names, and dynamic details in attributes.
Match the public span naming convention before adding custom business spans:
canonical names get semantic colors, labels, and built-in trace metric support.

## Phase 3: Add High-Value Attributes

Use the canonical attributes from `../references/span-schema.md`.

Minimum valuable set:
- `stt`: `transcript`, `metrics.ttfb`, `stt.confidence` when available
- `stt.provider.<name>`: `stt.providerName`, `metrics.ttfb`, `stt.confidence`, error status when a provider fails
- `llm`: `metrics.ttfb`, `llm.finish_reason`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, model/provider metadata when available
- `tts`: `metrics.ttfb`, provider/voice metadata when safe
- `llm_tool_call`: `function.name`, `tool_call_id`, `function.arguments` if safe and bounded, `tool.latency_ms`, numeric `tool.error`, numeric `tool.dependency_unavailable`, `tool.result.count` when applicable
- `conversation`: `tool.call.count`, `tool.failure.count`, numeric `workflow.completed`, numeric `workflow.dependency_blocked`, numeric `workflow.fallback_used` when the session boundary is available
- custom spans: one numerical attribute that can become a custom trace metric, such as `duration_ms`, `retry_count`, `confidence_score`, `queue_wait_ms`, or `external_api_latency_ms`

Set OTel status to `ERROR` on failing provider/tool/API spans. Coval custom trace metrics can calculate `error_rate` and `success_rate` from span status.

Also emit numeric `0`/`1` flags for important rates. Some public metric
creation APIs require a numeric `metric_attribute`; `average` over these flags
preserves the rate while still working in those environments.

## Phase 4: Protect Customers

Before committing enrichment, remove or bound:
- API keys, tokens, passwords, session cookies, account secrets, and credentials
- raw audio blobs or base64 audio
- full prompts/responses when they may contain PII
- unbounded transcripts in custom attributes unrelated to `stt.transcript`
- high-cardinality span names
- duplicated successful export retries

Prefer summaries and counts:
- `tool.result.count`
- `tool.result.success`
- `tool.error`
- `tool.call.count`
- `tool.failure.count`
- `workflow.completed`
- `workflow.dependency_blocked`
- `workflow.fallback_used`
- `prompt.message_count`
- `response.length`
- `http.status_code`
- `retry_count`

## Phase 5: Verify Improved Value

After changes:
1. Run one representative simulation or conversation through the Coval CLI/API,
   or reuse the in-flight validation run if it exercises the changed code.
2. Poll through the CLI/API until the run finishes and trace data appears. While
   it is pending, prepare candidate metrics or documentation notes instead of
   waiting idle.
3. Open the Coval trace viewer.
4. Confirm the trace has meaningful hierarchy and expected span colors.
5. Check Trace Search can filter by span name, status, duration, provider, or attributes.
6. If new numerical attributes were added, run `configure-trace-metrics` to create at least one metric against them after the span/attribute is visible in real trace data.

Report before/after differences in concrete terms, such as span count, new span names, new attributes, and the specific debugging question the trace can now answer.
