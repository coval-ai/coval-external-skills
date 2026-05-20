# Coval Tracing Reference

## Evergreen Public References

Prefer these public sources when the skill needs current API, SDK, or product
behavior beyond the local agent repo:

- Coval docs home: https://docs.coval.dev/getting-started/welcome
- Documentation index for AI agents: https://docs.coval.dev/llms.txt
- OpenTelemetry traces guide: https://docs.coval.dev/concepts/simulations/traces/opentelemetry
- API reference: https://docs.coval.dev/api-reference
- Python SDK examples: https://github.com/coval-ai/coval-examples/tree/main/python-sdk
- TypeScript SDK examples: https://github.com/coval-ai/coval-examples/tree/main/typescript-sdk

Use docs and SDK examples as current public reference material. Do not require
local access to Coval internal repos, and do not copy example-agent source code
into a customer repository. When implementation details differ between a skill
reference and the public docs/API, fetch the current docs, OpenAPI spec, or SDK
example and treat the live public source as authoritative.

## Ingestion

- Endpoint: `https://api.coval.dev/v1/traces`
- Method: `POST`
- Auth header: `x-api-key` or `X-API-Key`
- Target header: exactly one of `X-Simulation-Id` or `X-Conversation-Id`
- Content: OTLP trace JSON (`resourceSpans`) or OTLP protobuf (`application/x-protobuf`)
- Timeout: use 30 seconds

`X-Simulation-Id` must be the simulation output ID for a single simulation result, not the run ID. `X-Conversation-Id` is for conversation monitoring after `POST /v1/conversations:submit` returns a `conversation_id`.

## Server Behavior

Coval validates the API key, resolves the target against the authenticated organization, parses OTLP, and writes every span to ClickHouse. Storage is append-only. There is no deduplication if a client resends spans that already succeeded.

Responses to expect:

| Status | Meaning |
|--------|---------|
| 200 | Spans accepted |
| 400 | Missing both target headers, both target headers sent, invalid OTLP, or `X-Conversation-Id` used for a non-monitoring conversation |
| 401 | Missing or invalid API key |
| 403 | API key lacks `traces:write` |
| 404 | Simulation output or conversation not found, usually wrong ID or wrong org key |
| 413 | Payload too large; split the export |
| 500 | Storage or server error |
| 503 | Temporary database routing/storage unavailability; retry later |

## Payload Size And Retry

Keep each export comfortably below 3-4 MB. For buffered conversation exports or high-volume spans, use `BatchSpanProcessor` or equivalent with bounded batch size. Lower the batch size when spans include large attributes.

Retry only the failed batch. Retrying a batch that Coval already accepted duplicates spans in the trace viewer and double-counts trace-backed metrics.

## Conversation Monitoring Flow

Production conversations do not have a Coval simulation output ID at call start.

1. Buffer spans during the call.
2. Submit transcript/audio metadata with `POST /v1/conversations:submit`.
3. Read `conversation_id` from the response.
4. Export buffered spans to `/v1/traces` with `X-Conversation-Id`.
5. Attach audio later with `PATCH /v1/conversations/{conversation_id}` when the recording URL arrives, if needed.

## Coval UI Surfaces

- Result trace viewer: run result page -> OTel Traces card -> View Traces
- Direct simulation result route: `/runs/<run-id>/results/<simulation-output-id>/traces`
- Trace Search: organization-wide search across simulation and conversation traces
- Transition Hotspots: run-level or search-level transition/failure heatmap when traced data exists
- Custom Trace Metrics: query span names and span attributes from traced simulations

Trace Search supports filters by time range, span name, provider, status, duration, attributes, agent, and test set. Natural language search can translate queries such as "slowest 10 LLM calls in the last 24 hours" into filters.

## Existing Import Integrations

If the customer already uses Langfuse or Arize Phoenix and Coval is configured to import those traces, avoid adding a second exporter unless the customer explicitly wants native Coval OTLP export. Prefer one trace owner per process, or add Coval as an additional exporter to the existing OpenTelemetry provider.

## Secret Handling

Never print raw Coval API keys. Also treat Coval agent API responses as sensitive: some agent `metadata` fields can contain model/provider API keys. Redact `metadata` before quoting or attaching agent inventory output.
