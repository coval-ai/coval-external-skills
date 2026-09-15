# Can DTMF latency live as a persistent in-dashboard metric?

Short answer: not today. Use this skill per run — it is the reliable way to
measure DTMF-to-response latency.

## Why

- Coval's custom metric types (LLM judges, regex, tool-call checks, pause
  analysis, metadata extraction) include none that compute a timestamp
  difference between two transcript turns.
- The built-in statistical metrics measure related but different things:
  **Latency** averages all user-turn-to-agent-turn silence gaps across the
  call, and **Time to First Audio** measures from recording start to the
  first audible sound. Neither isolates the gap after a DTMF press.
- An LLM-judge metric cannot approximate it either: the transcript rendered
  to judge metrics includes tool-call turns but not per-turn timestamps, so a
  judge prompt has no timing data to do the math with.

## What to do instead

- Run `/dtmf-latency <run-id>` after each evaluation run. The computation is
  deterministic (transcript timestamps via the API), so results are stable
  and auditable.
- A built-in statistical DTMF Latency metric has been requested. If this
  matters for your rollout, tell your Coval contact — it helps prioritize.
