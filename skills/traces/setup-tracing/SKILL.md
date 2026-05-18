---
name: setup-tracing
description: Configure an AI agent to send OpenTelemetry traces to Coval. Use when a user wants to add Coval tracing, instrument an agent for simulations or conversation monitoring, make traces show up in Coval, handle SIP/PSTN/WebSocket trace correlation, or replace the one-command wizard with a security-reviewable manual setup.
---

# Setup Coval Tracing

Set up tracing in the customer's agent with the smallest additive change that produces a real Coval trace, then verify that trace against the agent's actual Coval connection path.

## Preflight

1. Confirm the agent repo or service scope. In a monorepo, do not instrument every service unless the user explicitly asks.
2. Check Coval authentication without reading secret files:
   ```bash
   coval whoami
   coval agents list --format json
   ```
   If the CLI is unavailable, use `COVAL_API_KEY` from the user's shell environment and direct API calls. Never print or store the raw key. When listing agents through the API, redact `metadata` before showing output because some provider integrations store model API keys there.
3. Fetch current API shape before writing API integrations:
   ```bash
   curl -fsS https://api.coval.dev/v1/openapi
   ```
4. Read the shared references before editing:
   - `../references/coval-tracing-reference.md`
   - `../references/agent-type-routing.md`
   - `../references/span-schema.md`

## Phase 1: Read-Only Analysis

Do not edit files until this phase is complete.

Identify:
- language and package manager
- app start command and one representative local invocation
- agent framework or provider stack: Pipecat, LiveKit, Vapi, Twilio, WebSocket, direct OpenAI/Anthropic, custom loop, etc.
- Coval agent type and connection path: SIP inbound, PSTN inbound, outbound voice, WebSocket voice/chat, or conversation monitoring
- where a per-call Coval ID can enter the agent process
- existing telemetry owner: OpenTelemetry, Sentry, Datadog, Honeycomb, Langfuse, Arize, LangSmith, Traceloop, or custom OTLP exporter
- short-lived process behavior and shutdown/flush path

Return a concise analysis summary. If the target service or correlation path is ambiguous, ask the user before editing.

## Phase 2: Pick The Correlation Path

Use exactly one target header per export:
- simulations: `X-Simulation-Id` with the simulation output ID
- conversation monitoring: `X-Conversation-Id` with the `conversation_id` returned by `POST /v1/conversations:submit`

Choose the route from `../references/agent-type-routing.md`:
- SIP inbound voice: extract `X-Coval-Simulation-Id` from SIP headers or framework participant attributes.
- PSTN inbound phone: do not expect SIP headers. Add or configure `pre_call_webhook_url` / registration-webhook correlation, or guide the customer to provision a SIP address.
- Outbound voice: carry `simulation_output_id` in the trigger payload and read it in the trigger handler.
- WebSocket voice/chat: carry the simulation output ID in the initial setup payload or initialization JSON.
- Conversation monitoring: buffer spans during the call, submit the conversation at call end, then export buffered spans with `X-Conversation-Id`.

## Phase 3: Implement Additive Instrumentation

Prefer an existing telemetry owner. If the app already has a `TracerProvider`, add a Coval exporter/processor to it instead of replacing the provider. If there is no telemetry setup, create one central module such as `coval_tracing.py`, `covalTracing.ts`, or `coval_tracing.go`.

Implementation requirements:
- Endpoint: `https://api.coval.dev/v1/traces`
- Auth header: `x-api-key` or `X-API-Key` from an environment variable, never a literal secret
- Timeout: 30 seconds
- Resource: set `service.name` to the agent or service name
- Export one target header only: `X-Simulation-Id` or `X-Conversation-Id`
- Buffer spans only when the Coval ID is not yet available; bound the buffer
- Use `BatchSpanProcessor` or equivalent for high-volume agents and keep batches comfortably below 3-4 MB
- Flush/shutdown tracing before short-lived processes exit
- Retry only failed batches; Coval stores spans append-only and does not deduplicate successful retries

For Python voice agents, the Coval wizard's generated `coval_tracing.py` pattern is an acceptable baseline, but improve it for the discovered connection path and existing telemetry.

## Phase 4: Minimum Span Coverage

The first working trace should contain:
- a root `conversation` or equivalent session span when the framework gives a call boundary
- at least one `stt`, `llm`, `tts`, or `llm_tool_call` span that matches the actual agent path
- correct parent/child relationships where the framework exposes them
- `service.name` resource metadata
- Coval-compatible target ID routing

If the app cannot expose STT/TTS/LLM internals yet, ship the minimum useful trace first, then use `optimize-trace-observability` for enrichment.

## Phase 5: Verification

Run local checks first:
```bash
python -m compileall .
npm test
npm run typecheck
go test ./...
```
Use the checks that match the repo; do not invent package-manager commands.

Then prove Coval ingestion:
1. Run one real agent interaction through the same Coval agent type the customer uses.
2. Confirm the trace export returns 200. A 404 from the standalone test script only proves auth/connectivity, not lifecycle wiring.
3. Open the Coval run or conversation result and verify the OTel Traces card or Trace Search result appears.
4. Inspect the trace for expected spans and attributes.

Optional connectivity-only check:
```bash
python skills/traces/setup-tracing/scripts/send-test-span.py \
  --api-key "$COVAL_API_KEY" \
  --simulation-id wizard-test
```
A 404 with `Simulation output not found` means the key reached Coval and auth worked, but it is not proof that the agent call lifecycle is wired.

## Handoff

End with:
- files changed and why
- exact correlation path used
- how the customer sets required env vars
- commands run
- Coval trace URL or simulation/conversation ID used for proof
- any remaining gaps to handle with `optimize-trace-observability`, `configure-trace-metrics`, or `debug-traces`
