---
name: build-test-suite
description: >
  Build a complete test suite with test set and test cases for evaluating an AI
  agent. Guides through test set type selection, scenario design using
  vertical-specific templates, expected behavior crafting, and bulk creation.
  Use when user says "create test cases", "build test suite", "add test
  scenarios", "set up evaluation tests", or "design test cases".
argument-hint: "[agent-name-or-use-case]"
---

# Build Test Suite

Guide the user through building a complete test suite — test set + test cases with expected behaviors — for evaluating an AI agent using the `coval` CLI. Follow the phases below in order, asking questions at each step.

If `$ARGUMENTS` contains an agent name or use case, use it to skip or pre-fill questions in Phases 1-2.

## Phase 0: Setup + Preflight

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
coval agents list --format json
coval test-sets list --format json
```

Note existing agents and test sets for reference throughout the flow.

## Phase 1: Agent Context

Ask: "Which agent are these tests for?"

- If agents exist, present a numbered list and let the user pick or say "new"
- If `$ARGUMENTS` matches an agent name, select it automatically

Fetch the selected agent's details:

```bash
coval agents get <agent_id> --format json
```

Capture from the response:
- `agent_id`
- `model_type` (voice, chat, etc.)
- `prompt` (system prompt, if available)
- `display_name`

If the agent has a system prompt, use it later to generate more specific, domain-relevant test scenarios instead of generic templates.

## Phase 2: Test Set Type Selection

Load `references/test-set-types.md` and present the available types.

Ask: "What type of test set do you want to create?"

- **SCENARIO** is the default and best for most use cases
- Explain when each type is appropriate based on the reference
- If the user is unsure, recommend SCENARIO

> **Note:** Test set type is not configurable via the CLI — all test sets default to SCENARIO type. To create other types, use the API: `POST /v1/test-sets` with a `test_set_type` field.

Then ask:
1. "What would you like to name this test set?" — suggest: `"<Agent Name> Evaluation"`
2. "Brief description?" — suggest based on agent type and use case

Create the test set:

```bash
coval test-sets create --name "<name>" --description "<desc>" --format json
```

Capture `test_set_id` from the JSON response.

## Phase 3: Scenario Design

Load `references/test-case-templates.md` and select the templates matching the agent's vertical/use case.

Present the 3-category pattern:
- **happy_path** — The standard, successful interaction
- **edge_case** — Unusual or challenging situations
- **compliance** — Regulatory, policy, or safety requirements

If the agent has a system prompt, customize the scenarios to be specific to the agent's domain rather than using generic templates. For example, if the agent handles dental appointments, tailor scenarios to dental-specific situations.

Present a summary table before creating:

```
Test Set: "<name>"

  [happy_path]   <test case name>
                 <scenario description>
  [edge_case]    <test case name>
                 <scenario description>
  [compliance]   <test case name>
                 <scenario description>
```

Ask: "Create these test cases? (yes / customize / add more)"

- **yes** → proceed to Phase 4
- **customize** → let the user edit scenarios, then re-present
- **add more** → generate additional scenarios, then re-present

## Phase 4: Expected Behaviors

For each test case, help craft an `expected_behaviors` array. These are what the Composite Evaluation metric scores against.

**Good expected behaviors are:**
- Specific — describes a concrete action or output
- Observable — can be verified from the conversation transcript
- Binary — it either happened or it didn't

**Examples of GOOD expected behaviors:**
- "Agent verifies caller identity before sharing account details"
- "Agent provides a confirmation number"
- "Agent offers at least two alternative time slots"
- "Agent does NOT share information from a different policy"

**Examples of BAD expected behaviors (avoid these):**
- "Agent is helpful" — too vague
- "Agent sounds nice" — subjective
- "Agent handles the situation well" — not observable

Present each test case with its expected behaviors for confirmation. Let the user add, remove, or edit behaviors.

## Phase 5: Bulk Creation

Create each test case:

```bash
coval test-cases create \
  --test-set-id <test_set_id> \
  --input '<scenario text>' \
  --expected "Agent greets the customer professionally" \
  --expected "Agent verifies caller identity" \
  --expected "Agent resolves the issue or escalates" \
  --description "<test case name>" \
  --format json
```

Pass each expected behavior as a separate `--expected` flag. This ensures they are stored as individual items in the `expected_behaviors` array, which the Composite Evaluation metric scores individually.

> **Shell tip:** Use single quotes for `--input` values to avoid shell interpolation issues (e.g., `$45.99` becoming `.99`).

If the CLI does not support multiple `--expected` flags, use the Coval API directly for structured expected behaviors:

```bash
curl -s -X POST https://api.coval.dev/v1/test-cases \
  -H "X-API-Key: $COVAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "test_set_id": "<test_set_id>",
    "input_str": "<scenario text>",
    "expected_behaviors": [
      "Agent greets the customer professionally",
      "Agent verifies caller identity",
      "Agent resolves the issue or escalates"
    ],
    "description": "<test case name>"
  }'
```

Present progress as each test case is created. Capture `test_case_id` from each response.

## Phase 6: Coverage Summary + Next Steps

Present what was created:

```
Test Suite Complete!

  Test Set:     <name> (<test_set_id>)
  Test Cases:   <N> total
    [happy_path]   <count>
    [edge_case]    <count>
    [compliance]   <count>
```

### Coverage Analysis

Review the test cases and suggest areas that might need more coverage:
- Are there common failure modes not covered?
- Are there regulatory requirements specific to the vertical?
- Would the agent benefit from multi-turn conversation tests?
- Are there language/accent scenarios worth testing (for voice agents)?

### Suggested Next Steps

- Design a test persona: `/design-persona`
- Configure evaluation metrics: `/configure-metrics`
- Launch a quick evaluation: `/quick-eval`
- Add more test cases later:
  ```bash
  coval test-cases create --test-set-id <test_set_id> --input "..." --expected "..." --description "..."
  ```
