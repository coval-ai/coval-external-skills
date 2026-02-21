---
name: quick-eval
description: Full evaluation workflow - launch a run, watch progress, and summarize results. Use for end-to-end agent testing.
argument-hint: "[agent] [test-set]"
---

# Quick Evaluation

Run a complete evaluation for `$ARGUMENTS`: launch, monitor, and summarize results.

## Workflow

### Step 1: Select Resources

List and confirm resources:

```bash
coval agents list
coval test-sets list
coval personas list
```

Confirm with user:
- Agent to evaluate
- Test set to use
- Persona for simulation

### Step 2: Launch Run

```bash
coval runs launch \
  --agent-id <agent_id> \
  --persona-id <persona_id> \
  --test-set-id <test_set_id> \
  --name "Quick Eval - $(date +%Y%m%d-%H%M)"
```

Capture the run ID from output.

### Step 3: Watch Progress

```bash
coval runs watch <run_id>
```

Wait for completion.

### Step 4: Gather Results

```bash
coval runs get <run_id> --format json
coval simulations list --run-id <run_id> --format json
```

### Step 5: Summarize

Present a summary:

```
## Evaluation Complete

**Run:** <run_id>
**Agent:** <agent_name>
**Test Set:** <test_set_name>
**Duration:** X minutes

### Results
- Total Simulations: N
- Completed: N
- Failed: N

### Sample Simulations
[List 3-5 simulation IDs for review]

### Next Steps
- View full results: `coval simulations list --run-id <run_id>`
- Download audio: `coval simulations audio <sim_id> -o recording.wav`
- Get transcript: `coval simulations get <sim_id>`
```
