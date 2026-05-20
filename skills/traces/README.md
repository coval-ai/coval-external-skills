# Traces

Skills for configuring, improving, measuring, and debugging Coval OpenTelemetry traces.

| Skill | Description |
|-------|-------------|
| [setup-tracing](./setup-tracing/) | Add Coval trace export and prove one real trace reaches Coval |
| [optimize-trace-observability](./optimize-trace-observability/) | Enrich trace spans and attributes for debugging and built-in metrics |
| [configure-trace-metrics](./configure-trace-metrics/) | Create custom trace metrics from span names and attributes |
| [debug-traces](./debug-traces/) | Troubleshoot missing traces, ingestion errors, and sparse trace data |

Trace metric work should finish with customer-signal metrics, not only
proof-of-ingest metrics. The metrics playbook includes recipes for dependency
blocked rate, tool failure rate, tool latency, workflow completion, fallback,
and per-conversation tool volume.

The shared reference files in `./references/` are intentionally detailed. Skill entrypoints load only the references needed for the current task.

For current platform behavior, trace setup should also consult the public Coval
docs and SDK examples linked from
[`references/coval-tracing-reference.md`](./references/coval-tracing-reference.md).
