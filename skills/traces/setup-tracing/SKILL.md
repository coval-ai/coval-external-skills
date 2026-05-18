---
name: setup-tracing
description: Configure an AI agent to send OpenTelemetry traces to Coval. Use when a user wants to add Coval tracing, instrument an agent for simulations or conversation monitoring, make traces show up in Coval, handle SIP/PSTN/WebSocket trace correlation, or replace the one-command wizard with a security-reviewable manual setup.
---

# Setup Coval Tracing

Set up tracing in the customer's agent with the smallest additive change that produces a real Coval trace, then verify that trace against the agent's actual Coval connection path.

Operate from the customer's agent side. Do not assume access to Coval internal
backend, frontend, docs, wizard, research, or example source repositories, and
do not ask the customer for them. Use only the customer's repo, public Coval
docs, the Coval CLI/API, and fetched public OpenAPI specs. Code edits belong in
the customer's agent/service repo. Coval-side changes must be limited to
documented configuration through the Coval CLI, public API, or dashboard, and
should be explained before mutation.

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
4. Stay inside the customer-owned code surface. Do not reference or require
   `coval-ai/backend`, `coval-ai/frontend`, `coval-ai/docs`,
   `coval-ai/wizard`, internal engineering docs, or Coval example repos as
   local source code. Public docs and installed skill reference files are the
   support material available to the customer-side agent.
5. Read the shared references before editing:
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
- customer-owned files that need edits, and any Coval configuration changes
  that must be done through CLI/API/dashboard rather than code changes

Return a concise analysis summary. If the target service or repo scope is
ambiguous, ask before editing. Do not ask the customer to choose a correlation
route from a menu. Customers usually cannot know whether SIP headers, pre-call
webhooks, or trigger payloads are supported from the outside; infer the best
route from the discovered agent configuration and the decision rules below.

## Phase 2: Pick The Correlation Path

Use exactly one target header per export:
- simulations: `X-Simulation-Id` with the simulation output ID
- conversation monitoring: `X-Conversation-Id` with the `conversation_id` returned by `POST /v1/conversations:submit`

Pick the route yourself when the repo and Coval agent configuration make one
route clearly safer. Do not present an open-ended "which route should I use?"
question. Use this decision order:

1. If the current connection path already delivers a Coval ID into the process,
   use that path. Examples: SIP participant attributes, outbound trigger
   payload, WebSocket initialization payload, or a monitoring
   `conversation_id`.
2. If the current Coval agent record or fetched OpenAPI confirms an existing
   pre-call/registration webhook field and the service already exposes a
   suitable endpoint, configure or reuse that webhook.
3. For inbound PSTN phone agents with no verified SIP headers and no confirmed
   Coval pre-call webhook wiring, default to a self-contained registration
   endpoint plus a smoke launcher that registers `simulation_output_id` right
   before the call. This is the safest first validation because it does not
   guess at Coval agent metadata shape or mutate customer agent config. After it
   works, state the production upgrade: wire the same endpoint into the verified
   Coval pre-call webhook field when available, or provision SIP if the customer
   needs Coval-managed per-call injection.
4. Ask a customer question only when every viable route requires a policy or
   deployment decision you cannot infer, such as whether you may expose a new
   public webhook, update the Coval agent configuration, or provision a SIP
   route. In that case, give one recommendation first, explain why, and ask for
   the smallest approval needed.

Choose the route from `../references/agent-type-routing.md`:
- SIP inbound voice: extract `X-Coval-Simulation-Id` from SIP headers or framework participant attributes.
- PSTN inbound phone: do not expect SIP headers. Add or configure `pre_call_webhook_url` / registration-webhook correlation, or guide the customer to provision a SIP address.
- Outbound voice: carry `simulation_output_id` in the trigger payload and read it in the trigger handler.
- WebSocket voice/chat: carry the simulation output ID in the initial setup payload or initialization JSON.
- Conversation monitoring: buffer spans during the call, submit the conversation at call end, then export buffered spans with `X-Conversation-Id`.

For direct WebSocket agents, prefer configuring Coval metadata with an explicit initialization payload such as:

```json
{"simulation_id": "{{simulation_id}}"}
```

Then treat the first non-audio frame as setup metadata, extract `simulation_id` or
`simulation_output_id`, and only export with `X-Simulation-Id` after that ID is
present. Current production examples use `{{simulation_id}}`; if docs mention
`{{simulation_output_id}}`, verify current agent metadata behavior before
hardcoding either name.

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
- Update deployment packaging. Dockerfiles, serverless bundles, Pipecat Cloud
  packages, and Fly/Render/Heroku deploys must include any new tracing helper
  module and dependency files.

For Python voice agents, an existing generated `coval_tracing.py` helper in the
customer repo is an acceptable baseline, but improve it for the discovered
connection path and existing telemetry.

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

Then start the Coval validation through CLI/API and do useful work while it
runs. Coval simulations and monitoring conversations are asynchronous; do not
sit idle after launching one.

1. Use the discovered Coval CLI/API path to launch one real test through the
   same Coval agent type the customer uses. Prefer CLI commands when available;
   otherwise use the public API after fetching OpenAPI. Capture the run ID,
   simulation output ID, conversation ID, dashboard URL, or polling endpoint
   returned by the launch.
2. Start a bounded poll loop through the CLI/API. Record the command or endpoint
   used, poll interval, and timeout. Do not print API keys or raw provider
   metadata from Coval agent responses.
3. While the run is pending, continue with non-blocking trace improvement:
   - add safe span enrichment visible from the code path, such as stable
     `conversation`, `turn`, `stt`, `llm`, `tts`, `llm_tool_call`,
     `transport`, or provider spans
   - add bounded high-value attributes such as `metrics.ttfb`, token counts,
     finish reasons, tool names, safe tool argument summaries, status, and
     errors
   - improve flush/shutdown, buffering, batch size, retry, or deployment
     packaging issues found during implementation
   - prepare custom trace metric candidates from expected spans and any
     historical Coval traces already available
4. Create custom trace metrics during the wait only when real trace data already
   proves the span name and metric attribute exist, either from historical
   traced runs or from the in-flight validation once spans appear in Trace
   Search. If this validation is the first trace for the agent, stage the metric
   definitions while waiting and create them immediately after the run produces
   confirmed spans.
5. When the run finishes, confirm the agent export returned 200 or that the
   exporter logged a successful accepted batch. A 404 from the standalone test
   script only proves auth/connectivity, not lifecycle wiring.
6. Open the Coval run or conversation result and verify the OTel Traces card or
   Trace Search result appears.
7. Inspect the trace for expected spans and attributes. If it is missing, sparse,
   duplicated, or attached to the wrong result, stop further metric creation and
   apply `debug-traces` before continuing.
8. After the initial trace is confirmed, finish any prepared metric creation and
   run one follow-up calculation/preview/attached-run check through the CLI/API
   when the public API supports it.

For WebSocket agents, make the smoke interaction long enough to trigger the
agent's response threshold. A client that sends too little audio, or an agent
that waits for more silence/audio than Coval sends, can make tracing look broken
even when the exporter is wired correctly. If a `tts` span is marked `ERROR`
with a WebSocket disconnect after partial audio, shorten the canned response or
stop streaming when the client closes.

Optional connectivity-only check:
```bash
python skills/traces/setup-tracing/scripts/send-test-span.py \
  --api-key "$COVAL_API_KEY" \
  --simulation-id coval-tracing-test
```
A 404 with `Simulation output not found` means the key reached Coval and auth worked, but it is not proof that the agent call lifecycle is wired.

## Handoff

End with:
- files changed and why
- exact correlation path used
- how the customer sets required env vars
- commands run, including the Coval launch and polling commands/API endpoints
- Coval trace URL or simulation/conversation ID used for proof
- custom trace metrics created, staged, or deferred and why
- any remaining gaps to handle with `optimize-trace-observability`, `configure-trace-metrics`, or `debug-traces`
