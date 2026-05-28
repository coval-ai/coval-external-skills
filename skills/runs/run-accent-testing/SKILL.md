---
name: run-accent-testing
description: End-to-end Coval accent testing workflow. Creates one persona per accent (each using a distinct accent voice and mirroring your Standard Customer behavior), launches one run per accent against the same voice agent + test set + metrics, polls for completion, and produces the multi-run report URL grouped by Persona. Use when a user wants to follow the Testing Across Accents cookbook (https://docs.coval.dev/guides/testing-across-accents) without doing each step by hand.
argument-hint: "[agent-name-or-id] [test-set-name-or-id]"
metadata:
  author: coval-ai
  version: "1.0.0"
  homepage: https://docs.coval.dev/guides/testing-across-accents
  source: https://github.com/coval-ai/coval-external-skills
---

# Run Accent Testing

Set up and launch a Coval accent testing sweep end-to-end: one voice agent, one
test set, an accent persona pack, shared metrics, and a multi-run report grouped
by **Persona**. Mirrors the public cookbook at
https://docs.coval.dev/guides/testing-across-accents.

Unlike the audio-quality pack, **the accent personas are not built-in**. This
skill creates them in the user's organization, one per accent voice, and makes
each one mirror the org's **Standard Customer** behavior so the only variable
between runs is the speaker's accent.

When the runs complete this skill hands off to
[analyze-accent-report](../../reports/analyze-accent-report/) for the
recommended-fixes write-up.

## When To Use

- The user wants to follow the "Testing Across Accents" cookbook but does not
  want to hand-create personas and hand-launch each run.
- The user has a voice agent (PSTN, SIP, WebSocket, LiveKit, Vapi, OpenAI
  Realtime, Gemini Realtime, etc.) and a test set they trust.
- The user wants a multi-run report URL grouped by Persona that they can save,
  share, or pass to the analysis skill.

Do **not** use this skill for chat-only agents. Accent testing exercises speech
recognition (STT) and audio timing, none of which a chat agent runs.

## Prerequisites

```bash
coval --version    # CLI must be installed (brew install coval-ai/tap/coval)
coval whoami       # must be authenticated to the right org
```

If `coval whoami` fails, run `coval login` first.

## Accent Persona Pack

The cookbook compares one neutral baseline against six accent personas. Each
accent persona uses a distinct accent voice; every other setting mirrors the
baseline so differences come from the accent, not behavior.

| Persona Name | `--voice` | Accent |
|---|---|---|
| Standard Customer | (built-in baseline) | Neutral baseline |
| Indian Accent (Vidya) | `vidya` | Indian |
| Scottish Accent (Chris) | `chris` | Scottish |
| Chinese Accent (Jay) | `jay` | Chinese-accented |
| US Southern Accent (Cletus) | `cletus` | US Southern |
| Nigerian Accent (Kehinde) | `kehinde` | Nigerian |
| Spanish Accent (Lisa) | `lisa` | Spanish-accented |

> **Low concurrency is expected.** All six accent voices are lower-concurrency
> ElevenLabs voices, and ElevenLabs voice simulations are globally capped per
> organization. Launch these runs at a **low `--concurrency` (2 is a safe
> default)** and expect simulations to queue and finish more slowly than a
> standard sweep. This is normal for this suite — it is not a failure.

## Workflow

### Step 1: Confirm The Voice Agent

If `$ARGUMENTS` includes an agent name or ID, look it up. Otherwise list voice
agents and ask the user to pick one:

```bash
coval agents list --format json | jq '.[] | select(.model_type | test("VOICE|REALTIME|WEBSOCKET")) | {id, display_name, model_type}'
```

Pick exactly one. The cookbook is explicit: **keep the agent configuration
fixed across all runs**. Confirm with the user before continuing.

If the agent emits OpenTelemetry traces, recommend including trace-based STT and
timing metrics in step 3. If not, recommend setting up traces (see
[Coval traces docs](https://docs.coval.dev/concepts/simulations/traces/opentelemetry))
or proceeding with transcript-and-audio-only metrics such as Transcription
Error.

### Step 2: Confirm The Test Set

```bash
coval test-sets list
```

Pick one test set. The same test set must be used across every persona run.
Subsampling is allowed as long as the **same sampled cases** run across all
seven personas — use a fixed `--sub-sample-seed` (e.g. `42`) and the same
`--sub-sample-size` on every run.

### Step 3: Confirm Metrics

Accent testing is primarily a **speech-recognition** stress test: does the agent
correctly understand accented speech, and does any mis-recognition change the
task outcome? Lead with STT, then task outcome and call shape. Reuse any metrics
the agent already has attached when they fit.

| Goal | Useful Metrics |
|---|---|
| Speech recognition (headline) | STT Word Error Rate for traced agents, or Transcription Error for audio-backed conversations |
| Task outcome | Composite evaluation, task-completion LLM judges, or scenario-specific pass/fail metrics |
| Responsiveness | Latency, time to first audio, trace TTFB, provider response-time |
| Conversation flow | Turn count, repeated confirmation/clarification loops, early termination, silence, interruption rate |

Do **not** include `manager_audio_frequency` — it measures signal
characteristics, not accent comprehension.

Do **not** recommend `STT Word Error Rate (Audio Upload)` for this general
workflow. It only applies when the test set uses uploaded audio with reference
transcripts, which is a different setup from the normal voice-simulation sweep.

```bash
coval metrics list
```

Collect the chosen metric IDs into a comma-separated string for the launch step.
If the user wants to use the agent's default metrics, omit `--metric-ids`
entirely on the launch call.

### Step 4: Ensure The Accent Personas Exist

The accent personas are not built-in, so create any that are missing. Make each
one mirror the org's **Standard Customer** so the only variable is the accent
voice.

First resolve Standard Customer and read its behavior prompt and language:

```bash
STD_ID=$(coval personas list --filter 'name:"Standard Customer"' --format json \
  | jq -r '.[] | select(.name == "Standard Customer") | .id' | head -1)

if [ -n "$STD_ID" ]; then
  STD=$(coval personas get "$STD_ID" --format json)
  STD_PROMPT=$(echo "$STD" | jq -r '.persona_prompt // ""')
  STD_LANG=$(echo "$STD"   | jq -r '.language_code // ""')
fi

# Fallbacks if Standard Customer is missing or has no prompt/language.
if [ -z "$STD_LANG" ] || [ "$STD_LANG" = "null" ]; then
  STD_LANG="en-US"
fi
if [ -z "$STD_PROMPT" ] || [ "$STD_PROMPT" = "null" ]; then
  STD_PROMPT="You are a standard customer calling in with a routine request. Speak naturally and conversationally. Answer the agent's questions, provide the information it asks for, and work toward completing your task."
fi
```

Then create each accent persona only if an exact-name match does not already
exist (idempotent — never create duplicates):

```bash
# "Persona Name|voice" — the voice is the Coval catalog name.
ACCENTS=(
  "Indian Accent (Vidya)|vidya"
  "Scottish Accent (Chris)|chris"
  "Chinese Accent (Jay)|jay"
  "US Southern Accent (Cletus)|cletus"
  "Nigerian Accent (Kehinde)|kehinde"
  "Spanish Accent (Lisa)|lisa"
)

for entry in "${ACCENTS[@]}"; do
  name="${entry%%|*}"
  voice="${entry##*|}"

  existing=$(coval personas list --filter "name:\"$name\"" --format json \
    | jq -r --arg n "$name" '.[] | select(.name == $n) | .id' | head -1)

  if [ -n "$existing" ]; then
    echo "exists: $name ($existing)"
    continue
  fi

  echo "creating: $name (voice: $voice)"
  coval personas create \
    --name "$name" \
    --voice "$voice" \
    --language "$STD_LANG" \
    --prompt "$STD_PROMPT" \
    --format json
done
```

Notes:

- The `--voice` value is the lowercase Coval catalog name (`vidya`, `chris`,
  `jay`, `cletus`, `kehinde`, `lisa`), not the display label.
- Reuse the **same** `--prompt` and `--language` for every accent persona so the
  accent voice is the only thing that changes between runs.
- Do not overwrite an existing persona. If one already exists with a different
  voice or prompt, tell the user and let them decide — do not silently recreate.

### Step 5: Resolve Persona IDs

Resolve all seven persona IDs by exact-name match (Standard Customer plus the
six accent personas) into ordered arrays the launch step reuses. Keep Standard
Customer first so it is the baseline column in the report:

```bash
# Canonical persona order — Standard Customer first (baseline).
PERSONA_NAMES=(
  "Standard Customer"
  "Indian Accent (Vidya)"
  "Scottish Accent (Chris)"
  "Chinese Accent (Jay)"
  "US Southern Accent (Cletus)"
  "Nigerian Accent (Kehinde)"
  "Spanish Accent (Lisa)"
)

PERSONA_IDS=()
for name in "${PERSONA_NAMES[@]}"; do
  id=$(coval personas list --filter "name:\"$name\"" --format json \
    | jq -r --arg n "$name" '.[] | select(.name == $n) | .id' | head -1)
  if [ -z "$id" ]; then
    echo "MISSING persona: $name — resolve Step 4 before launching" >&2
    exit 1
  fi
  PERSONA_IDS+=("$id")
  echo "$id  $name"
done
```

If any persona is still missing after Step 4, the loop stops — fix it before
launching. Do not skip an accent.

### Step 6: Launch The Runs

Launch seven runs — one per persona — with the same agent, test set, metrics,
and (if subsampling) the same `--sub-sample-seed`. Keep `--concurrency` low
because these are lower-concurrency voices. Use shared tags so the runs are easy
to find later.

```bash
SUB_SAMPLE_SEED=42
SUB_SAMPLE_SIZE=0   # 0 = all cases; set to a positive integer to subsample
CONCURRENCY=2       # low on purpose — accent voices are lower-concurrency
TAGS="accent-testing,cookbook"
metric_args=()
if [ -n "${METRIC_IDS:-}" ]; then
  metric_args=(--metric-ids "$METRIC_IDS")
fi

# Uses PERSONA_NAMES / PERSONA_IDS from Step 5; captures each run_id into RUN_IDS.
RUN_IDS=()
for i in "${!PERSONA_IDS[@]}"; do
  persona_id="${PERSONA_IDS[$i]}"
  persona_name="${PERSONA_NAMES[$i]}"
  resp=$(coval runs launch \
    --agent-id "$AGENT_ID" \
    --persona-id "$persona_id" \
    --test-set-id "$TEST_SET_ID" \
    "${metric_args[@]}" \
    --concurrency "$CONCURRENCY" \
    --sub-sample-size "$SUB_SAMPLE_SIZE" \
    --sub-sample-seed "$SUB_SAMPLE_SEED" \
    --tags "$TAGS" \
    --name "Accent — $persona_name" \
    --format json)
  run_id=$(echo "$resp" | jq -r '.run_id // .id')
  RUN_IDS+=("$run_id")
  echo "launched $persona_name -> $run_id"
done
```

The loop appends each launched `run_id` to `RUN_IDS`, which Step 7 watches and
Step 8 turns into the report URL.

**Tip:** the public API also supports a batch launch (`POST /v1/runs/batch`) if
you prefer one HTTP call. The CLI does not expose batch launch today.

### Step 7: Watch For Completion

```bash
for run_id in "${RUN_IDS[@]}"; do
  coval runs watch "$run_id"
done
```

`coval runs watch` blocks until the run reaches a terminal status (COMPLETED,
FAILED, or CANCELLED). Because the accent voices are lower-concurrency,
simulations may queue and the sweep may take longer than a standard run — that
is expected. Run these in parallel shells or background jobs if you want all
seven watched at once.

If any run finishes as **FAILED** with `total_test_cases=0`, the run-setup
worker crashed before sub-sampling. Re-launch that single run with
`--sub-sample-size 1` (or omit subsampling) and report the failure as a Coval
issue — this has been observed in some orgs.

### Step 8: Build The Multi-Run Report URL

Concatenate the seven run IDs and produce the report URL:

```bash
RUN_IDS_CSV=$(IFS=,; echo "${RUN_IDS[*]}")
ORG_SLUG=$(coval whoami --format json | jq -r '.organization.slug')
echo "https://app.coval.dev/${ORG_SLUG}/reports/new?run_ids=${RUN_IDS_CSV}"
```

Tell the user to:

1. Open the URL.
2. Set **Compare by** to **Persona**.
3. Save the report with a descriptive name (this preserves the grouping for
   future viewers).
4. If they want to share without a Coval login, use the report's **Share**
   button to publish a shareable link.

### Step 9: Hand Off Analysis

Once the report is saved, point the user at
[analyze-accent-report](../../reports/analyze-accent-report/) for a structured
next-fix write-up. The analysis skill turns the grouped report into prompt,
STT/confirmation, routing, or coverage recommendations.

Suggest pasting the saved report URL into:

```text
Use the Coval `analyze-accent-report` skill on this report:
<paste saved report URL>
```

## Output Format

When the skill finishes, return a short, actionable summary:

```markdown
## Accent Testing — Launch Summary

**Agent:** <display_name> (<id>)
**Test set:** <display_name> (<id>)
**Subsample:** <sub_sample_size> cases (seed <sub_sample_seed>) — or "full test set"
**Metrics:** <comma-separated metric names>
**Personas created this run:** <list, or "none — all already existed">

**Runs:**
| Persona | Voice | Run ID | Status | Run link |
|---|---|---|---|---|
| Standard Customer | (baseline) | … | … | https://app.coval.dev/<org>/runs/<id> |
| Indian Accent (Vidya) | vidya | … | … | … |
| Scottish Accent (Chris) | chris | … | … | … |
| Chinese Accent (Jay) | jay | … | … | … |
| US Southern Accent (Cletus) | cletus | … | … | … |
| Nigerian Accent (Kehinde) | kehinde | … | … | … |
| Spanish Accent (Lisa) | lisa | … | … | … |

**Multi-run report:**
https://app.coval.dev/<org>/reports/new?run_ids=<csv> — open and set **Compare by → Persona**, then save.

**Next step:** run the `analyze-accent-report` skill on the saved report.
```

## Guardrails

- One agent, one test set, same metrics, same subsample seed across all seven
  runs. Any divergence breaks the grouped comparison the report depends on.
- Make every accent persona mirror Standard Customer's prompt and language. The
  accent voice must be the only variable, or the comparison is not interpretable.
- Create accent personas only when an exact-name match is missing. Never create
  duplicates, and never silently overwrite an existing persona.
- Keep `--concurrency` low and expect queueing — these are lower-concurrency
  voices. Slow completion is expected, not a failure.
- Do not change the agent's configuration mid-sweep. If you must, launch a fresh
  sweep so the comparison stays apples-to-apples.
- Do not use chat-only agents. The cookbook explicitly does not apply.
- Do not skip an accent because the org "doesn't serve" that population. The full
  pack is what makes the comparison interpretable.
- Do not invent persona, agent, test set, or metric IDs — always resolve them
  from the user's org.
