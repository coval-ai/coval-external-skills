---
name: onboard
description: >
  Interactively set up a first Coval AI evaluation. Guides users through
  installing the CLI, connecting an agent, creating personas, building test
  cases, selecting metrics, and launching their first eval run. Use when user
  says "onboard", "get started", "set up evaluation", "first eval", "new to
  coval", or wants help creating their first test run.
argument-hint: "[use-case]"
compatibility: Requires the Coval CLI (coval). The skill will guide installation if missing.
metadata:
  author: coval-ai
  version: "1.0.0"
  homepage: https://coval.dev
  source: https://github.com/coval-ai/coval-external-skills
---

# Coval Onboarding

Guide the user through setting up a complete AI evaluation from scratch using the `coval` CLI. Follow the phases below in order, asking questions at each step.

If `$ARGUMENTS` contains a use case (e.g. "insurance_claims", "customer_support"), skip the use case question in Phase 2.

## Phase 0: Setup + Preflight

### Step 1: Check CLI installation

```bash
which coval
```

If the CLI is not installed, guide the user to install it:

**macOS (Homebrew):**
```bash
brew install coval-ai/tap/coval
```

**macOS/Linux (Cargo — requires Rust):**
```bash
cargo install coval
```

**All platforms (binary download):**
Download the latest release for your OS from https://github.com/coval-ai/cli/releases

After installation, verify: `coval --version`

### Step 2: Check authentication

```bash
coval whoami
```

If not authenticated, guide the user:
```bash
coval login
```
This prompts for an API key. Get one at https://app.coval.dev/settings (Organization > Manage > API Keys).

If the user doesn't have a Coval account, direct them to https://coval.dev to sign up.

Then run these in parallel to inventory existing resources:

```bash
coval agents list --format json
coval test-sets list --format json
coval metrics list --format json
coval personas list --format json
```

**Decision matrix:**
- No resources → full flow (Phases 1-6)
- Has agents but nothing else → ask which agent to use, skip Phase 1
- Has agents + test sets → ask which to reuse, skip Phases 1 & 3
- Has everything → ask "Re-launch existing eval or build new?"

Present existing resources as a numbered list and let the user pick or say "new".

## Phase 1: Connect Agent

Ask these questions:

1. "What type of AI agent do you have?"
   - `voice` — Receives inbound phone calls
   - `outbound-voice` — Your agent calls out
   - `chat` — Text/API endpoint
   - `sms` — SMS-based agent
   - `websocket` — WebSocket connection

2. Based on type:
   - voice / sms → "What is your agent's phone number? (E.164 format, e.g. +12345678901)"
   - outbound-voice / chat / websocket → "What is your agent's endpoint URL?"

3. "What would you like to name this agent?"

4. (Optional) "Do you have the agent's system prompt? Pasting it helps generate better test cases."

Create the agent:

```bash
# For voice/sms:
coval agents create --name "<name>" --type <type> --phone-number "<number>" --format json

# For chat/outbound-voice/websocket:
coval agents create --name "<name>" --type <type> --endpoint "<url>" --format json
```

Capture `agent_id` from the JSON response.

## Phase 2: Discover Use Case + Create Persona

Ask these questions:

1. "What does your agent do?"
   - customer_support — Customer Support
   - scheduling_booking — Scheduling & Booking
   - sales — Sales
   - insurance_claims — Insurance Claims
   - healthcare_intake — Healthcare Intake
   - restaurant_orders — Restaurant Orders
   - debt_collection — Debt Collection
   - it_helpdesk — IT Helpdesk
   - other — Other (describe it)

2. "What industry is this for?" (free text)

3. "What language does your agent speak?"
   - en-US, es-ES, fr-FR, de-DE, pt-BR, ja-JP

4. "What's the #1 thing your agent must get right?" (free text — this becomes a custom metric)

Load `references/persona-templates.md` and select the persona template matching the use case. Apply the user's language choice. Present the persona to the user for confirmation before creating.

```bash
coval personas create \
  --name "<persona_name>" \
  --voice "<voice_name>" \
  --language "<language_code>" \
  --prompt "<behavior_prompt>" \
  --background "<background_sound>" \
  --wait-seconds <wait> \
  --format json
```

Capture `persona_id` from the JSON response.

For chat/sms/websocket agents, still pass `--voice` and `--language` with defaults (aria, en-US) — these fields are ignored by the simulation engine for non-voice agents.

## Phase 3: Create Test Set + Test Cases

Load `references/test-case-templates.md` and select the 3 test case templates (happy_path, edge_case, compliance) matching the use case.

If the user provided a system prompt or critical requirement, customize the test cases to be more specific to their agent.

Present a summary table before creating:

```
Test Set: "<Use Case> Evaluation"

  [happy_path]   <test case name>
                 <scenario description>
  [edge_case]    <test case name>
                 <scenario description>
  [compliance]   <test case name>
                 <scenario description>
```

Ask: "Create these test cases? (yes / customize / add more)"

Create the test set and cases:

```bash
coval test-sets create --name "<Use Case> Evaluation" --description "<desc>" --format json
```

Capture `test_set_id`. Then for each test case:

```bash
coval test-cases create \
  --test-set-id <test_set_id> \
  --input "<scenario text>" \
  --expected "<expected behaviors joined with newlines>" \
  --description "<test case name>" \
  --format json
```

Note: The `--expected` flag accepts a single string. Join the expected behaviors array with newlines (`\n`).

## Phase 4: Select + Create Metrics

Load `references/metric-recommendations.md` and build the metric list.

**Always recommend:**
- Composite Evaluation (built-in) — find its ID from the `coval metrics list` output in Phase 0

**Use-case specific (from recommendations):**
- One custom llm-binary metric per vertical (e.g. "Identity Verification" for insurance)

**Critical requirement:**
- If the user provided one in Phase 2, create an additional llm-binary metric with that requirement as the prompt

**Voice agents only:**
- Professional Tone (audio-binary)
- Pause Detection (pause, min 3.0s)

**Default built-ins** (reference by existing ID):
- Latency, Call Resolution, Sentiment

Present the recommendations:

```
Based on your <use case> agent, I recommend these metrics:

  [built-in]  Composite Evaluation    — Evaluates expected behaviors per test case
  [custom]    <Use Case Metric>       — <description>
  [custom]    <Critical Requirement>  — Based on your #1 priority
  [audio]     Professional Tone       — Agent tone quality (voice only)
  [audio]     Pause Detection         — Flags pauses > 3 seconds (voice only)
```

Ask: "Accept these metrics? (yes / add more / remove some)"

Create custom metrics:

```bash
# LLM Binary metric
coval metrics create \
  --name "<metric name>" \
  --description "<description>" \
  --type llm-binary \
  --prompt "<evaluation prompt>" \
  --format json

# Pause metric (voice only)
coval metrics create \
  --name "Long Pause Detection" \
  --description "Flags pauses longer than 3 seconds" \
  --type pause \
  --min-pause-duration 3.0 \
  --format json
```

Collect all metric IDs (built-in + newly created).

## Phase 5: Create Template + Launch

Ask:
1. "How many iterations per test case? (1 for a quick first look, 3 for statistical confidence)" — default: 1
2. "How many parallel simulations? (1-5)" — default: 3

Create the run template for reuse:

```bash
coval run-templates create \
  --name "First Eval - <Use Case>" \
  --agent-id <agent_id> \
  --persona-id <persona_id> \
  --test-set-id <test_set_id> \
  --metric-ids <comma_separated_ids> \
  --iteration-count <iterations> \
  --concurrency <concurrency> \
  --format json
```

Launch the evaluation:

```bash
coval runs launch \
  --agent-id <agent_id> \
  --persona-id <persona_id> \
  --test-set-id <test_set_id> \
  --metric-ids <comma_separated_ids> \
  --iterations <iterations> \
  --concurrency <concurrency> \
  --name "First Eval - <Use Case>" \
  --format json
```

Capture `run_id` from the response.

## Phase 6: Watch + Results

Watch the run:

```bash
coval runs watch <run_id>
```

When complete, fetch results:

```bash
coval runs get <run_id> --format json
coval simulations list --filter "run_id=\"<run_id>\"" --format json
```

For each simulation, fetch metrics:

```bash
coval simulations metrics <simulation_id> --format json
```

Present a summary:

```
Evaluation Complete!

  Run:          First Eval - <Use Case>
  Test Cases:   <count>
  Iterations:   <count>
  Status:       COMPLETED

  Results:
  | Test Case                    | Score | Status |
  |------------------------------|-------|--------|
  | Happy Path — <name>          | 0.85  | PASS   |
  | Edge Case — <name>           | 0.60  | WARN   |
  | Compliance — <name>          | 1.00  | PASS   |

  View full results: https://app.coval.dev/runs/<run_id>

  Saved as template: "First Eval - <Use Case>"
  Re-run: coval runs launch --agent-id <id> --persona-id <id> --test-set-id <id>
```

Suggest next steps:
- Add more test cases: `coval test-cases create --test-set-id <id> --input "..."`
- Schedule recurring runs: `coval scheduled-runs create --template-id <id> --schedule "cron(0 9 * * MON)"`
- Listen to recordings: `coval simulations audio <sim_id> -o recording.wav`
- Iterate on metrics based on results
