---
name: dtmf-latency
description: >
  Measure DTMF keypress-to-response latency from Coval simulation transcripts.
  Computes the time from each DTMF tone (e.g. pressing 1 in an IVR menu) to the
  bot's first spoken response, deterministically from transcript timestamps —
  no OTel or tracing setup required. Use when user says "dtmf latency",
  "keypress latency", "how long after pressing 1", "IVR response time",
  "connection time after DTMF", or "measure DTMF response".
argument-hint: "[run-id or simulation-id]"
---

# DTMF Latency

Measure DTMF-to-first-response latency for `$ARGUMENTS`.

All timing math is done by the bundled script — render its JSON output
faithfully and **never recompute or estimate numbers yourself**.

## Step 0: Verify Authentication

```bash
coval whoami
```

If not authenticated, run `coval login` (get an API key at
https://app.coval.dev/settings under Organization > Manage > API Keys).

For raw API fallback, resolve the key in this order: `coval config get api-key`,
then `~/.config/coval/config.json`, then the `COVAL_API_KEY` env var.

## Step 1: Resolve Input

- **No argument**: list recent runs with `coval runs list --page-size 10` and
  ask the user which run to analyze.
- **Argument provided** (run and simulation IDs are both 22 chars): try
  `coval simulations get <id> --format json` first; if not found, treat it as
  a run ID.

**Run path**: the simulations list endpoint does not include transcripts, so
fetch each simulation's detail individually:

```bash
coval simulations list --run-id <run_id> --format json
```

Then for each simulation ID, save the detail JSON to a temp directory:

```bash
coval simulations get <sim_id> --format json > <tmpdir>/<sim_id>.json
```

Raw API fallback: `curl -s -H "X-API-Key: $KEY" https://api.coval.dev/v1/simulations/<sim_id>`

For runs with more than 20 simulations, tell the user how many you are
fetching. Include FAILED/empty simulations — the script counts them as
"not analyzable" rather than silently dropping them.

## Step 2: Compute

```bash
python3 <skill-dir>/scripts/dtmf_latency.py <tmpdir>/*.json
```

Options:
- `--digits 1` — only measure events where exactly those digits were pressed
- `--timeout-threshold 15` — latencies at/above this are always flagged as outliers
- `--debug` — list every tool-call name seen (use when no DTMF is detected)

The script emits a JSON report: per-simulation events, aggregates
(min/p50/p95/max), and outliers. Event statuses: `OK`, `TIMEOUT` (bot never
responded after the keypress — reported as a lower bound, excluded from
averages), `NO_TIMESTAMPS`. Burst presses (e.g. an account number) are
collapsed into one event, anchored at the last press. Events with
`user_spoke_first: true` mean the caller spoke again before the bot responded
— the latency spans that user turn, so treat it as "bot never acknowledged the
keypress" rather than a clean response time, and call this out in the report.

## Step 3: Report

Start with a verdict line and bucket summary built from the script's
`aggregate.buckets` (never recompute), then one section per run ID using the
`by_run` stats:

```markdown
**Verdict:** N of M keypresses were acknowledged within 4s; X were never
acknowledged (the caller gave up and spoke first) and Y got no response at
all before the call ended.

**Distribution:** <1s: 9 · 1–4s: 8 · >4s: 0 · never acknowledged: 4 · timeout: 1

## Run <run_id>

| Simulation ID | DTMF Press (s) | Agent Speaks (s) | Latency (s) |
|---|---|---|---|
| [<sim_id>](<sim_url>) | 10.42 | 12.73 | 2.31 |
| [<sim_id>](<sim_url>) | 35.10 | — | TIMEOUT (>14.5) |

**Latency:** average 2.4s · median 2.3s · min 0.4s · max 3.3s
(N measured events; T timeouts excluded from stats)
```

One table row per DTMF event: `pressed_end` → DTMF Press, `response_start` →
Agent Speaks, `latency` → Latency. TIMEOUT events show "—" and the
`latency_lower_bound`. Append "(caller spoke first)" to rows with
`user_spoke_first: true`.

**Simulation links**: the app URL is
`https://app.coval.dev/<org-slug>/runs/<run_id>/results/<simulation_id>`.
The org slug is the first path segment the user sees when logged into
app.coval.dev (it is not available via the API) — ask for it once if you
don't know it. If the slug is unknown, render plain simulation IDs without
links.

After the per-run sections, if there were TIMEOUT or `user_spoke_first`
events, add a short "Flags" note — the bot never acknowledged those presses,
usually the most important finding. Mention counts of simulations skipped as
NO_DTMF or not analyzable.

## If No DTMF Events Are Found

Show this checklist — the setup must satisfy all of it for the metric to work:

- The persona/test config must emit DTMF as **tool calls** (transcript turns
  with `is_tool_call=true`, a name containing `dtmf`, `tool_call_owner="user"`).
  A persona that merely *says* "I press one" produces nothing measurable.
- Transcript turns must carry `start_time`/`end_time` (voice simulations;
  chat-only runs may not have them).
- Simulations must be COMPLETED with non-empty transcripts, and the bot's
  speech must appear as non-tool `assistant` turns.

Run the script with `--debug` and check whether keypresses appear under a
different tool name; report what you find.

## If Asked About a Persistent In-Dashboard Metric

Not currently possible: no Coval metric type computes timestamp differences,
and the transcript rendered to LLM judge metrics does not include per-turn
timestamps, so a judge metric cannot do the math either. Use this skill per
run. Details: `references/persistent-metric.md`.

## Next Steps

- Listen to an outlier call: `/download-audio <sim_id>`
- Review a full transcript: `/get-results <sim_id>`
- Re-run after agent changes: `/launch-run`, then `/dtmf-latency <new_run_id>`
