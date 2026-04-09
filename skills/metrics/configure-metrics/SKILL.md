---
name: configure-metrics
description: >
  Select and configure evaluation metrics for an AI agent. Guides through
  metric selection using use-case recommendations, custom LLM-based metric
  creation with prompt engineering, and agent default attachment. Use when user
  says "set up metrics", "configure metrics", "create a metric", "what metrics
  should I use", "add evaluation criteria", or "customize scoring".
argument-hint: "[agent-name-or-use-case]"
---

# Configure Metrics

Guide the user through selecting, creating, and attaching evaluation metrics for their AI agent using the `coval` CLI. Follow the phases below in order.

If `$ARGUMENTS` contains an agent name or use case, use it to skip the relevant question in Phase 1.

## Phase 0: Preflight + Inventory

### Step 1: Check authentication

```bash
coval whoami
```

If not authenticated, guide the user:
```bash
coval login
```
This prompts for an API key. Get one at https://app.coval.dev/settings (Organization > Manage > API Keys).

If the user doesn't have a Coval account, direct them to https://coval.dev to sign up.

### Step 2: Inventory existing resources

Run these in parallel:

```bash
coval metrics list --format json
coval metrics list --include-builtin --format json
coval agents list --format json
```

Categorize the metrics inventory:
- **Built-in**: Metrics with `created_by: "Coval"` in the `--include-builtin` response. These are platform-provided and exist in every org (e.g., Latency, Turn Count, Audio Duration, Transcript Sentiment Analysis, etc.)
- **Custom**: User-created metrics (llm-binary, audio-binary, pause types)

Note the IDs of relevant built-in metrics — you'll need them for Phase 5.

## Phase 1: Agent + Use Case Context

Ask:

1. "Which agent are these metrics for?"
   - Present existing agents as a numbered list from the inventory
   - If `$ARGUMENTS` matches an agent name, select it automatically

2. "What does your agent do?" (if not obvious from agent name or prompt)
   - customer_support — Customer Support
   - scheduling_booking — Scheduling & Booking
   - sales — Sales
   - insurance_claims — Insurance Claims
   - healthcare_intake — Healthcare Intake
   - restaurant_orders — Restaurant Orders
   - debt_collection — Debt Collection
   - it_helpdesk — IT Helpdesk
   - other — Other (describe it)

Capture the agent's `type` (voice, outbound-voice, chat, etc.) from the agent record — this determines whether audio metrics apply.

## Phase 2: Metric Recommendations

Load `references/metric-recommendations.md` and build the recommendation list.

**Built-in metrics** (discover dynamically from `coval metrics list --include-builtin --format json`, look for `created_by: "Coval"`):
- Select relevant built-ins based on agent type:
  - **All agents**: Latency, Turn Count
  - **Voice agents**: Audio Duration, Transcript Sentiment Analysis, Audio Sentiment, Speech Tempo, Time To First Audio, Interruption Rate, Background Noise
  - **Chat agents**: Words Per Message, Transcript Sentiment Analysis

**Use-case specific:**
- One custom llm-binary metric per vertical (from recommendations file)

**Voice agents only** (type = voice or outbound-voice):
- Professional Tone (audio-binary) — custom, needs creation
- Pause Detection (pause, min 3.0s) — custom, needs creation

Present the recommendations:

```
Based on your <use case> agent, I recommend these metrics:

  [built-in]  Latency                 — Response time measurement
  [built-in]  Turn Count              — Number of conversation turns
  [built-in]  <other relevant built-ins based on agent type>
  [custom]    <Use Case Metric>       — <description from recommendations>
  [audio]     Professional Tone       — Voice quality (voice agents only)
  [audio]     Pause Detection         — Flags pauses > 3s (voice agents only)
```

> **Tip:** List all available built-ins with `coval metrics list --include-builtin --format json` and identify them by `created_by: "Coval"`. Recommend the ones most relevant to the user's agent type and use case.

Ask: "Accept these metrics? (yes / add more / remove some)"

- **yes** → proceed to Phase 3
- **add more** → ask what additional criteria they want to measure, add to list
- **remove some** → present numbered list, let them deselect

## Phase 3: Custom Metric Creation

For each custom metric in the accepted list, guide through creation:

1. **Name and description** — pre-filled from recommendations, confirm with user
2. **Type selection** — load `references/metric-types.md` if the user wants to understand options
3. **Configuration**:
   - For **llm-binary**: Use the prompt template from recommendations. Ask if they want to customize it.
   - For **audio-binary**: Use the prompt from recommendations. Customize if needed.
   - For **pause**: Confirm min duration threshold (default 3.0s).

Create each metric:

```bash
# LLM Binary metric
coval metrics create \
  --name "<name>" \
  --description "<description>" \
  --type llm-binary \
  --prompt "<evaluation prompt>" \
  --format json

# Audio Binary metric (voice only)
coval metrics create \
  --name "<name>" \
  --description "<description>" \
  --type audio-binary \
  --prompt "<prompt>" \
  --format json

# Pause metric (voice only)
coval metrics create \
  --name "<name>" \
  --description "<description>" \
  --type pause \
  --min-pause-duration 3.0 \
  --format json
```

Capture the `metric_id` from each JSON response.

## Phase 4: Critical Requirement Metric

Ask: "What's the #1 thing your agent MUST get right?"

If the user provides a requirement:
1. Create an additional llm-binary metric using the critical requirement template from `references/metric-recommendations.md`
2. **Convert the user's requirement into a short Title Case metric name** — do NOT use the raw requirement text as the name. Follow the built-in metric naming convention: short noun phrases like "Caller Identity Verification", "Issue Resolution", "Order Accuracy". Examples:
   - "The agent must verify caller identity before sharing account details" → `"Caller Identity Verification"`
   - "The agent should never promise features that don't exist" → `"Feature Claim Accuracy"`
   - "Make sure the agent collects the policy number" → `"Policy Number Collection"`
3. Use the user's full requirement text in the `--prompt` and `--description` fields — that's where the detail belongs.

```bash
coval metrics create \
  --name "<short Title Case name>" \
  --description "<user's full requirement text>" \
  --type llm-binary \
  --prompt "Given the transcript, did the agent satisfy this requirement: <user's requirement>? Return YES if the requirement was met. Return NO if the requirement was violated or not addressed." \
  --format json
```

Capture the `metric_id`.

If the user says "none" or "skip", proceed without creating this metric.

## Phase 5: Attach to Agent

Collect all metric IDs:
- Built-in metric IDs from Phase 0 inventory
- Newly created custom metric IDs from Phases 3 and 4

Offer to attach as agent defaults:

```
I'll attach these metrics as defaults for <agent name>:

  <metric name 1>  (<metric_id>)
  <metric name 2>  (<metric_id>)
  ...

These will automatically apply to every evaluation run for this agent.
```

Ask: "Attach these as defaults? (yes / no)"

If yes:

```bash
coval agents update <agent_id> --metric-ids <comma_separated_ids>
```

## Phase 6: Summary + Next Steps

Present all configured metrics:

```
Metrics configured for <agent name>:

  Type         Name                      ID
  ──────────   ────────────────────────  ──────────────────────
  built-in     Latency                   <id>
  built-in     Turn Count                <id>
  built-in     <other selected built-ins> <id>
  custom       <Use Case Metric>         <id>
  custom       <Critical Requirement>    <id>
  audio        Professional Tone         <id>
  audio        Pause Detection           <id>

  Attached to agent: <agent name> (<agent_id>)
```

Suggest next steps:
- Build test cases: "Use `/build-test-suite` to create test scenarios"
- Design persona: "Use `/design-persona` to create a simulated caller"
- Launch evaluation: "Use `/quick-eval` to run your first evaluation"
- **If new metrics were created**: "Use `/build-dashboard` to add your new metrics to a dashboard so you can track them visually"
