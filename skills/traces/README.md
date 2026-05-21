# Traces

Skills for configuring, improving, measuring, and debugging Coval OpenTelemetry traces.

| Skill | Description |
|-------|-------------|
| [setup-tracing](./setup-tracing/) | Add Coval trace export, launch a real validation run, and prove trace URLs + correlation |
| [optimize-trace-observability](./optimize-trace-observability/) | Enrich trace spans and attributes for debugging and built-in metrics |
| [configure-trace-metrics](./configure-trace-metrics/) | Create custom trace metrics and trace-aware LLM judge metrics, then verify they compute on a post-change run |
| [debug-traces](./debug-traces/) | Troubleshoot missing traces, ingestion errors, and sparse trace data |

Trace metric work should finish with customer-signal metrics, not only
proof-of-ingest metrics. The metrics playbook includes recipes for dependency
blocked rate, tool failure rate, tool latency, workflow completion, fallback,
per-conversation tool volume, and trace-aware LLM judge metrics with
`include_traces=true`.

The shared reference files in `./references/` are intentionally detailed. Skill entrypoints load only the references needed for the current task.

For current platform behavior, trace setup should also consult the public Coval
docs and SDK examples linked from
[`references/coval-tracing-reference.md`](./references/coval-tracing-reference.md).
