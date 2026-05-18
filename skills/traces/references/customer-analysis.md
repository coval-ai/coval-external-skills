# Public Skill Pattern Analysis

These notes summarize patterns to reuse when helping customers instrument Coval traces.

## Arize Skills

Arize separates first-time instrumentation from trace inspection/debugging. The instrumentation skill uses a two-phase flow: read-only stack analysis first, then implementation. It explicitly checks language, package manager, framework, providers, existing telemetry, tool usage, and verification path. It also prefers existing framework/native instrumentation and adds manual spans only for gaps such as tools or agent loops.

Reusable patterns for Coval:
- do a read-only analysis phase before edits
- never embed credentials
- preserve existing telemetry ownership
- route by detected framework and runtime
- verify that a real trace appears, not just that code changed
- keep a separate debugging skill for existing trace data

## Raindrop Workshop

Raindrop emphasizes "minimal useful run first, enrichment second." Its workshop skill verifies a local run appears before adding detailed spans. It also warns not to create competing providers when existing OTel/Sentry/Datadog/Honeycomb/LangSmith telemetry already owns tracing.

Reusable patterns for Coval:
- first prove one useful Coval trace
- then add STT/LLM/TTS/tool enrichment
- report progress and intended edits before changing files
- use installed package docs/types instead of stale memory when exact APIs matter

## Agent Observability Skills

The public agent-observability skill set splits observability into focused skills such as planning, LLM tracing, tool tracking, token/cost tracking, and error/retry tracking. It frames every span or metric around the question it answers: task success, latency, cost, failure cause, or decision path.

Reusable patterns for Coval:
- split setup, enrichment, metric creation, and debugging
- avoid full prompt/response capture by default
- prefer stable semantic span names and dot-notation attributes
- use focused metrics rather than measuring everything

## Coval-Specific Implications

Coval differs from generic LLM observability tools because trace value depends on call correlation and voice pipeline semantics:
- the customer must route the simulation output ID or conversation ID correctly
- SIP, PSTN, outbound, WebSocket, and monitoring flows need different correlation paths
- voice-native spans (`stt`, `tts`, provider attempts, transcript, TTFB) unlock Coval built-ins
- custom trace metrics depend on exact span names and numeric attributes in ClickHouse

Therefore, Coval tracing skills should be connection-path aware and should validate inside Coval, not only in a local trace viewer.
