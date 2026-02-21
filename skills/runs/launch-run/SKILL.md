---
name: launch-run
description: Launch a Coval evaluation run against an AI agent. Use when user wants to start an evaluation, test an agent, or run simulations.
argument-hint: "[agent-name-or-id] [test-set-name-or-id]"
---

# Launch Coval Evaluation Run

Launch an evaluation run for `$ARGUMENTS`.

## Prerequisites

Ensure the Coval CLI is installed and authenticated:
```bash
coval whoami
```

If not authenticated, run `coval login` first.

## Workflow

### Step 1: Identify Resources

If agent or test set not specified, list available options:

```bash
coval agents list
coval test-sets list
coval personas list
```

Ask user to select:
- **Agent**: Which agent to evaluate
- **Test Set**: Which test cases to run
- **Persona**: Which simulated user persona

### Step 2: Configure Run Options

Ask about optional parameters:

| Option | Flag | Default |
|--------|------|---------|
| Iterations per test case | `--iterations` | 1 |
| Concurrent simulations | `--concurrency` | 5 |
| Run name | `--name` | Auto-generated |
| Mutation (A/B variant) | `--mutation-id` | None |

### Step 3: Launch

```bash
coval runs launch \
  --agent-id <agent_id> \
  --persona-id <persona_id> \
  --test-set-id <test_set_id> \
  --iterations <n> \
  --concurrency <n> \
  --name "Descriptive Run Name"
```

### Step 4: Confirm

Report the run ID and status. Offer to watch progress:

> Run launched: `<run_id>`
> Status: IN QUEUE
>
> Would you like me to watch the progress?

If yes, use `coval runs watch <run_id>`.

## Example

```bash
coval runs launch \
  --agent-id abc123 \
  --persona-id xyz789 \
  --test-set-id ts456 \
  --iterations 3 \
  --concurrency 10 \
  --name "Q1 Regression Test"
```
