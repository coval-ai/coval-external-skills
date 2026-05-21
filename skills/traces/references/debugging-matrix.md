# Debugging Matrix

Use the first matching symptom, then verify the fix with a real Coval run or conversation.

| Symptom | Likely Cause | Check | Fix |
|---------|--------------|-------|-----|
| 400 missing target header | Neither `X-Simulation-Id` nor `X-Conversation-Id` sent | Inspect export headers | Send exactly one target header |
| 400 both target headers | Both headers sent | Inspect exporter setup | Split simulation and conversation flows |
| 400 invalid OTLP | Payload is not OTLP JSON/protobuf | Check body starts with `resourceSpans` for JSON | Use OpenTelemetry exporter or valid OTLP JSON |
| 400 non-monitoring conversation | `X-Conversation-Id` used for a normal run | Confirm conversation came from `conversations:submit` | Use `X-Simulation-Id` for simulations |
| 401 | Missing/invalid API key | `coval whoami`; standalone test span | Set valid Coval API key in env |
| 403 | API key lacks trace write permission | Response body details | Create/use key with `traces:write` |
| 404 simulation not found | Wrong ID, run ID instead of simulation output ID, or wrong org key | Compare result URL and API key org | Use simulation output ID and matching org key |
| 404 conversation not found | Wrong `conversation_id` or wrong org key | Check submit response | Use returned `conversation_id` |
| 413 | Export too large | Check payload size/buffered span count | Batch below 3-4 MB |
| 500 | Storage/server error | Response body and retry once | Retry failed batch only; escalate if persistent |
| 503 | Temporary routing/storage unavailable | Response status | Retry with backoff |
| No OTel card | No spans for that simulation output, wrong route, or export after user checked | Trace Search by simulation output ID | Fix ID routing and rerun |
| Trace exists but is sparse | Only provider auto-instrumentation or root span exists | Inspect span names | Run `optimize-trace-observability` |
| Trace rows are mostly `conversation` | Child spans were not emitted, span names are too broad, or only root-level events are instrumented | Inspect span-name distribution and parent/child tree | Add role-specific turn/tool/provider spans and bounded attributes |
| Duplicated spans | Successful batch resent | Compare identical span IDs/timestamps | Retry failed batches only; dedupe only in future exports |
| Custom trace metric says no spans | Span name mismatch or no traces in that simulation | Trace Search exact span name | Use emitted span name or fix instrumentation |
| Metric attribute missing | Attribute absent or non-numeric | Inspect trace detail | Emit numeric attr or choose span-level aggregation |
| Metric outputs stuck `IN QUEUE` while run still `IN PROGRESS` | Simulation finished but metric workers still computing | Poll run status and simulation metrics status | Wait for terminal run status and terminal metric outputs before concluding |
| Metric fails on old run but passes on new run | Metric definition or instrumentation changed after older run | Compare run create times and metric update time | Validate against first post-change run; treat older failures as stale evidence |
| Custom trace metric create rejects aggregation | Target API validation differs from docs or desired metric shape | Read response details and OpenAPI | Use accepted numeric fallback; document drift |
| PSTN inbound missing IDs | Expected SIP header on phone network | Inspect provider setup event | Use SIP or pre-call registration webhook |
| WebSocket missing IDs | Initialization/setup payload omitted simulation ID | Inspect first frame/setup request | Add simulation output ID to initialization JSON |
| WebSocket run has no assistant audio | Agent waited for more audio/silence than Coval sends | Compare received bytes to response threshold | Lower threshold or force response earlier |
| `tts` span shows WebSocket disconnect | Agent streamed after Coval closed the socket | Inspect span exception and sent byte counts | Shorten response or stop streaming on disconnect |
| Deployed agent cannot import tracing helper | Helper module/dependency not copied to image or bundle | Check deploy logs and Dockerfile/package manifest | Copy helper and dependency files into deploy artifact |
| Conversation traces missing | Spans exported before submit without conversation ID or never flushed | Inspect call-end flow | Buffer spans, submit, then export with `X-Conversation-Id` |

## Trace Search Queries

Useful searches:
- `errors from <agent name> in the last 24 hours`
- `slowest 10 LLM calls`
- `TTS calls longer than 2 seconds`
- span name `llm_tool_call` with status `ERROR`
- attribute exists `metrics.ttfb`
- provider equals the STT/TTS/LLM provider name

## Minimal OTLP JSON Shape

Use this only for debugging. Production code should use the OpenTelemetry SDK where possible.

```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "debug-agent"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {"name": "coval.debug"},
          "spans": [
            {
              "traceId": "00000000000000000000000000000001",
              "spanId": "0000000000000001",
              "name": "debug-validation-span",
              "kind": 1,
              "startTimeUnixNano": "1710000000000000000",
              "endTimeUnixNano": "1710000001000000000",
              "attributes": [],
              "status": {"code": 1},
              "events": [],
              "links": []
            }
          ]
        }
      ]
    }
  ]
}
```
