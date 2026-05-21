# Agent Type Routing

Use this reference to decide how the Coval simulation or conversation ID reaches the agent process.

## SIP Inbound Voice

Best path when available. Coval injects `X-Coval-Simulation-Id` as a SIP header. Frameworks surface it differently:

- LiveKit: participant attributes such as `sip.h.X-Coval-Simulation-Id`, `X-Coval-Simulation-Id`, or lowercase variants
- Pipecat/Daily dial-in: dial-in metadata or `args.body` SIP headers
- Telnyx or SIP webhooks: provider-specific SIP headers in the call event payload

Implementation pattern:
1. Initialize tracing before the call pipeline starts.
2. Buffer spans until the SIP participant/call event arrives.
3. Extract the simulation output ID.
4. Activate export with `X-Simulation-Id`.
5. Reset per-call exporter state when warm workers handle multiple calls.

## PSTN Inbound Phone

Standard phone-number routes, including Twilio Programmable Voice, do not preserve custom SIP headers. Do not wait for `X-Coval-Simulation-Id` on this path.

Supported options:
- Prefer SIP provisioning if the customer's voice stack can expose a SIP URI.
- Otherwise configure Coval `pre_call_webhook_url` to call a customer endpoint before dialing. The endpoint should queue `simulation_output_id` and match it to the incoming call by caller ID, call SID, or FIFO only when concurrency is controlled.

Decision rules:
- If the fetched Coval agent configuration already contains a verified
  `pre_call_webhook_url` or equivalent registration-webhook field, use that
  field. Patch only the confirmed field shape, and redact provider metadata in
  any output you show.
- If the repo already exposes an authenticated HTTP endpoint that Coval or a
  smoke launcher can call before the PSTN call, reuse it and store the
  `simulation_output_id` with a short TTL.
- If there is no verified Coval pre-call field yet, but the agent service can
  expose a small endpoint, choose an additive `POST /register-simulation`
  endpoint plus a smoke launcher as the first validation path. This is the
  recommended default for local/customer testing because it is self-contained,
  proves the trace exporter and PSTN correlation logic, and avoids guessing at
  Coval-side metadata shape.
- After the self-contained path works, recommend the durable production wiring:
  connect the same registration endpoint to the verified Coval pre-call webhook
  field when supported, or provision SIP when the customer needs Coval to inject
  the ID automatically for every simulation.
- Do not ask "FIFO or pre-call webhook?" as a customer-facing choice. Choose
  based on the current agent config. Ask only for a concrete missing permission,
  such as approval to expose a webhook, update the Coval agent config, or
  provision SIP.

Implementation pattern:
1. Add an authenticated registration endpoint such as `POST /register-simulation`.
2. Validate a shared secret or Coval API key header.
3. Store `simulation_output_id` with a short TTL and a bounded queue.
4. On call setup, match the queued ID to the incoming call.
5. Export call-end spans with `X-Simulation-Id`.

Safety rules for FIFO registration:
- Registration should queue the simulation ID; it should not immediately bind
  the ID to an arbitrary already-active provider call. Warm voice services can
  keep receiving stale `status-update`, `conversation-update`, or
  `speech-update` webhooks from an older call after a restart.
- Ignore low-signal provider events before a call state exists. For Vapi, do
  not create call state from `conversation-update`, `speech-update`,
  `user-interrupted`, or `status-update` alone.
- Claim a queued simulation ID only from a new or recent high-signal call event:
  call start/assistant request, live `tool-calls`, or final
  `end-of-call-report`. If the implementation supports late claim, bound it to
  a short recent-call window and log when a call closes without an ID.
- For local validation after `POST /v1/runs`, poll
  `GET /v1/simulations?filter=run_id%3D%22<RUN_ID>%22` and register the
  returned simulation output ID immediately. Do not wait for
  `GET /v1/runs/{run_id}` `results.output_ids` because that field can appear
  only after the call completes.
- State the concurrency limitation plainly. FIFO is acceptable for a
  single-call smoke test or controlled single-machine demo; production PSTN
  correlation should prefer a pre-call webhook with a provider call SID,
  caller-specific token, SIP route, or another deterministic join key.

## Outbound Voice

Coval triggers the customer's service with a POST. The service then places the call.

Implementation pattern:
1. Add `simulation_output_id` to Coval `trigger_call_payload`.
2. Read that field in the trigger endpoint.
3. Persist it through the provider call lifecycle using call SID/session ID.
4. Export spans with `X-Simulation-Id` when the call produces spans.

## WebSocket Voice Or Chat

Coval connects directly to the customer's WebSocket endpoint or uses an HTTP-first setup flow.

Implementation pattern:
1. Configure the Coval agent to pass the simulation output ID in
   initialization/setup payload. For direct JSON-audio WebSocket agents, a
   verified production shape is `{"simulation_id":"{{simulation_id}}"}`.
2. Read the ID from the first frame, setup response, or connection metadata before treating the connection as fully correlated.
3. Fail closed or log a clear warning if the ID is missing.
4. Export per-turn or call-end spans with `X-Simulation-Id`.

Use the placeholder supported by the current Coval agent configuration and
OpenAPI. Existing examples use `{{simulation_id}}` in `initialization_json`;
docs may also refer to `{{simulation_output_id}}`. Verify the current platform
field before hardcoding.

When validating, send enough audio to cross the agent response threshold and keep
canned responses short enough to finish before Coval closes the socket.
Otherwise the run can still ingest spans, but the trace may show interrupted
`tts` spans or no agent audio.

## Conversation Monitoring

Use when the customer evaluates live production conversations after the call.

Implementation pattern:
1. Start spans during the live call and buffer them locally.
2. Submit the transcript to `POST /v1/conversations:submit`.
3. Read `conversation_id`.
4. Export buffered spans with `X-Conversation-Id`.
5. Optionally attach audio later.

Do not use `X-Conversation-Id` for normal simulation runs. The backend rejects non-monitoring runs.

## Framework Notes

- Pipecat: prefer enabling framework tracing and enriching the standard spans. Copy helper instrumentation modules into Docker images.
- LiveKit: session event hooks can emit STT/LLM/TTS/tool spans. Reset exporter state per session.
- Vapi: end-of-call reports are useful for building a complete trace after the call. Read simulation ID from assistant override variables or SIP headers when available. For Vapi-hosted PSTN agents, see `vapi-artifact-tracing.md`: use real `tool-calls` webhooks for `llm_tool_call` spans, use `artifact.messages` for `turn` spans, and treat derived STT/LLM/TTS spans as metadata markers unless provider timing is explicitly exposed.
- Twilio ConversationRelay: usually PSTN, so use pre-call registration for simulations and conversation submit for monitoring.
- Custom WebSocket bridges: tag spans with the active simulation ID or route exporters per session so concurrent calls do not cross streams.
