# Vapi Artifact Tracing

Use this reference for Vapi-hosted agents, especially inbound PSTN agents where
the customer server receives Vapi webhooks but does not own the provider
STT/LLM/TTS pipeline.

## What Is Real

Vapi `end-of-call-report` and call APIs can expose an `artifact.messages`
array. Public Vapi call docs show message fields such as `role`, `message`,
`time`, `endTime`, `secondsFromStart`, and `duration`:
`https://docs.vapi.ai/api-reference/calls/get`.

Treat this as source data for:
- transcript text
- speaker role
- turn order
- turn timing windows when `secondsFromStart`, `endTime`, or `duration` is
  present
- safe per-message metadata Vapi includes, such as model, token counts, finish
  reason, or TTFB when present

Treat live `tool-calls` webhooks as source data for:
- real `llm_tool_call` spans
- tool handler latency measured in the customer process
- tool result status, error type, dependency failure, result count, and safe
  argument summaries
- root `conversation` attributes such as `tool.call.count`,
  `tool.failure.count`, `workflow.completed`,
  `workflow.dependency_blocked`, and `workflow.fallback_used`

## What Is Not Real Provider Timing

For Vapi-hosted PSTN agents, the customer webhook usually does not expose
provider-internal Deepgram/OpenAI/TTS span boundaries. Do not invent STT, LLM,
or TTS latency from a transcript message duration.

Good pattern:
- emit a `turn` span using the Vapi message window
- optionally emit tiny provider marker spans named `stt`, `llm`, and `tts` only
  when the trace viewer needs semantic labels, and mark them clearly:
  - `trace.source=vapi_artifact`
  - `trace.timing=metadata_marker`
  - `trace.duration_note=marker only; Vapi artifact does not expose provider
    <STT|LLM|TTS> latency`
- make marker spans visually tiny, for example 1 ms at the beginning or end of
  the turn

Safer alternative when the customer is likely to confuse markers for provider
latency:
- name them `stt_marker`, `llm_marker`, and `tts_marker`
- keep canonical `stt`/`llm`/`tts` only for measured provider operations or
  Vapi fields that explicitly expose provider timing

Bad pattern:
- giving `turn`, `stt`, `llm`, and `tts` identical full-message durations
- creating STT/LLM/TTS latency metrics from marker spans
- setting fake `stt.confidence`, fake TTFB, or hard-coded provider success
  values just to make the trace look rich

## Correlation Pattern For PSTN

If no verified Coval pre-call webhook field is available, use a self-contained
registration path for validation:

1. Add authenticated `POST /register-simulation`.
   - Require the same Coval API key in the `x-api-key` request header so the
     endpoint is not publicly writable.
   - Accept `simulation_output_id` in the JSON body (this is the simulation
     output ID returned by the Coval run, not the run ID itself).
   - Return `{"registered": true, "simulation_output_id": "<id>"}` on success.
2. Queue the Coval simulation output ID with a short TTL.
3. Keep at least one warm instance when the queue is in memory. Scale-to-zero
   clears the queue.
4. Lazily create a per-call trace state on the first useful Vapi webhook
   (`tool-calls`, `conversation-update`, `status-update`, or
   `end-of-call-report`). For inbound PSTN, `assistant-request` typically does
   not arrive at the customer server when Coval uses `vapi_assistant_id`
   directly — do not depend on it for session creation.
5. Claim the queued simulation ID by FIFO only when validation concurrency is
   controlled, or by call metadata when a stable match key exists.
6. At `end-of-call-report`, do a final late claim before export. This handles
   races where the call state opens before registration or registration arrives
   before the first webhook.
7. Export once with `X-Simulation-Id`; do not replay successful batches because
   Coval ingest is append-only.

After validation, recommend durable production wiring:
- connect the same registration endpoint to the verified Coval pre-call webhook
  field when available, or
- provision SIP if the customer needs per-call ID injection without FIFO.

## Vapi Timestamp Guardrails

When reconstructing turn spans from `artifact.messages`, Vapi timestamp fields
have known quirks that cause OTel int64 overflow or wrong span placement if not
guarded:

- **`startedAt` for call wall-clock anchor**: this field is on the
  `end-of-call-report` message envelope (`message["startedAt"]`), not on the
  nested `call` sub-object (which only has `createdAt`/`updatedAt`). Always
  read from the envelope first.
- **`time` field**: absolute Unix milliseconds, not seconds-from-start.
  Do not use `time` as a turn offset — multiplying by `1e9` overflows the OTel
  int64 nanosecond timestamp. Use `secondsFromStart` for offsets instead.
- **`secondsFromStart` anomaly**: most message types populate this as a small
  positive offset (e.g. `4.2` = 4.2 s into the call). However, some Vapi
  message types populate it with an absolute Unix-millisecond timestamp
  instead. Guard against this: if `secondsFromStart > 7200` (more than 2 hours
  into a call is implausible), skip or discard that message. Apply the same
  guard to `endTime`.

Safe turn span timing pattern:
```python
t_start = msg.get("secondsFromStart")
if t_start is None or t_start > 7200:
    continue  # skip messages with implausible offsets
t_end_raw = msg.get("endTime")
t_end = (t_end_raw if t_end_raw is not None and t_end_raw <= 7200
         else t_start + max(0.5, word_count * 0.35))
start_ns = int((call_start_epoch_s + t_start) * 1_000_000_000)
end_ns   = int((call_start_epoch_s + t_end)   * 1_000_000_000)
```

## Span Shape

Recommended Vapi PSTN trace:
- root `conversation`
- `vapi.webhook.<type>` or a low-cardinality webhook span/event for important
  webhook arrivals
- `llm_tool_call` for each Vapi tool call, with:
  - `function.name`
  - `tool_call_id`
  - safe bounded `function.arguments`
  - `tool.latency_ms`
  - numeric `tool.error`
  - numeric `tool.dependency_unavailable`
  - `tool.result.count`
  - `error.type` and ERROR status on failed tool calls
- **`turn.assistant` and `turn.user` spans** from `artifact.messages` (name
  encodes role so trace viewer rows are visually distinct; do not use a flat
  `turn` name for all messages):
  - `turn.role`: `"assistant"` or `"user"`
  - `turn.text`: first ~200 chars of the message content — makes the span
    readable directly in the trace viewer without opening the detail panel;
    do not include full transcripts as this can include PII at volume
  - `turn.word_count`: word count for verbosity metrics
  - `turn.content_length`: character count
  - `turn.seconds_from_start`: offset from call start (already used for timing;
    keep as attribute for turn-timeline metrics)
- provider marker spans only with explicit marker attributes, or marker-suffixed
  names
- root numeric attributes:
  - `tool.call.count`
  - `tool.failure.count`
  - `workflow.completed`
  - `workflow.dependency_blocked`
  - `workflow.fallback_used`
  - `user.interruption.count`

## Metric Implications

Create numeric custom trace metrics from real tool/workflow attributes:
- Tool Failure Rate: `llm_tool_call` / `tool.error` / `average` / `ratio`
- Tool Latency P90: `llm_tool_call` / `tool.latency_ms` / `p90` / `ms`
- Workflow Blocked Rate: `conversation` /
  `workflow.dependency_blocked` / `average` / `ratio`
- Workflow Completion Rate: `conversation` /
  `workflow.completed` / `average` / `ratio`
- Fallback Used Rate: `conversation` /
  `workflow.fallback_used` / `average` / `ratio`
- Tool Calls Per Conversation: `conversation` /
  `tool.call.count` / `average` / `count`

Do not create provider latency metrics from marker spans. Only create LLM/STT/TTS
latency metrics when the trace contains measured provider timing or explicit
provider timing fields.

Also create trace-aware LLM judge metrics when trace context helps evaluate
behavior that transcripts alone can miss:
- identity verification before account-specific tool calls
- tool-output grounding and no hallucinated claims after tool errors
- read-back or confirmation before using sensitive identifiers
- recovery after dependency failures or likely STT mistranscription

Use `include_traces: true` on LLM judge metric types when the live Metrics
OpenAPI supports it.
