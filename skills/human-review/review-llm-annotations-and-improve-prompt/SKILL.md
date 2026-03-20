---
name: review-llm-annotations-and-improve-prompt
description: Calculate agreement between human ground truth and machine labels for a text LLM judge metric, then analyze transcripts and reviewer notes to propose an improved metric prompt. One metric at a time.
argument-hint: <project_id> <metric_id>
---

# Improve Metric

Analyze human review annotations against machine-generated scores for a single text LLM judge metric. Calculate agreement, identify patterns in disagreements, and propose an improved metric prompt based on transcript analysis and reviewer feedback.

## Critical Rules

1. **NEVER update the metric prompt without explicit user approval.** Always present the proposed changes and wait for confirmation before running `coval metrics update`.
2. **Only operate on one metric at a time.** If the user provides a project with multiple metrics, ask which one to focus on.
3. **Only support text LLM judge metrics.** Valid types: `METRIC_LLM_BINARY`, `METRIC_CATEGORICAL`, `METRIC_NUMERICAL_LLM_JUDGE`. Reject audio metrics, toolcall, metadata, regex, pause, and composite types.
4. **NEVER fabricate data.** If a CLI command or API call fails, report the error — do not invent scores or transcripts.
5. **Use the CLI first, fall back to curl only when the CLI does not return required fields** (e.g., the LLM explanation under `result.llm.answer_explanation`).

## Usage

```
/review-llm-annotations-and-improve-prompt <project_id> <metric_id>
```

Both arguments are required. If the user omits one, ask for it.

---

## Phase 0: Validate Inputs

### Step 1: Fetch the metric and validate its type

```bash
coval metrics get <metric_id> --format json
```

Extract from the response:
- `metric_name` — the full display name
- `metric_type` — must be one of: `METRIC_LLM_BINARY`, `METRIC_CATEGORICAL`, `METRIC_NUMERICAL_LLM_JUDGE`
- `prompt` — the current evaluation prompt
- `min_value` / `max_value` — for numerical metrics only
- `categories` — for categorical metrics only

**If the metric type is not a text LLM judge, STOP and tell the user:**
> "This skill only supports text LLM judge metrics (binary, categorical, numerical). The metric `{metric_name}` is type `{metric_type}`, which is not supported."

### Step 2: Fetch the review project

```bash
coval review-projects get <project_id> --format json
```

Verify:
- The `linked_metric_ids` includes the target metric ID
- Note the assignees and linked simulation IDs

**If the metric is not linked to the project, STOP and tell the user.**

### Step 3: Present a summary before proceeding

> **Metric:** {metric_name} (`{metric_id}`)
> **Type:** {metric_type}
> **Current prompt:** "{prompt}"
> **Project:** {project_display_name} ({N} simulations, {M} assignees)
>
> Proceeding to gather annotations and calculate agreement.

---

## Phase 1: Gather Data

### Step 1: Gather annotations with ground-truth values for this metric in the project

Fetch both completed and all annotations in parallel:

```bash
# Completed annotations
coval review-annotations list \
  --filter 'project_id="{project_id}" AND metric_id="{metric_id}" AND completion_status="COMPLETED"' \
  --format json \
  --page-size 100

# All annotations (to find pending ones with ground-truth values)
coval review-annotations list \
  --filter 'project_id="{project_id}" AND metric_id="{metric_id}"' \
  --format json \
  --page-size 100
```

If there are more than 100 annotations in either list, paginate.

From the full list, identify **pending annotations that have a ground-truth value** — where `completion_status` is `PENDING` but `ground_truth_float_value` is not null OR `ground_truth_string_value` is not null. Reviewer notes are optional.

Present what was found:

> **Found {completed_count} completed annotations and {pending_with_value_count} pending annotations with ground-truth values.**

If there are pending annotations with values, ask:

> **{pending_with_value_count} pending annotations have ground-truth values but are not marked as completed. Would you like to include them in the analysis?** (yes/no)

- **If yes** — merge them into the dataset alongside completed annotations
- **If no** — proceed with only the completed annotations

**If zero usable annotations exist after this step, STOP:**
> "No annotations with ground-truth values found for this metric in this project. Reviewers need to submit ground-truth values before agreement can be calculated."

### Step 2: For each annotation, gather the full picture

For each annotation, collect these four pieces of data:

#### a) Ground truth and reviewer notes (already in the annotation)
- `ground_truth_float_value` or `ground_truth_string_value` — the human label
- `reviewer_notes` — the reviewer's reasoning (may be null)

#### b) Machine score
Use the annotation's `simulation_output_id` to get the machine-generated value:

```bash
coval simulations metrics <simulation_output_id> --format json
```

Find the metric output where `metric_id` matches the target metric. Extract `value` as the machine score.

#### c) Transcript
```bash
coval simulations get <simulation_output_id> --format json
```

Extract the `transcript` array. Format it as readable text:
```
[role]: content
[role]: content
...
```

#### d) LLM explanation (via API if not in CLI output)
The LLM's reasoning is stored in the metric output's `result` field under `result.llm.answer_explanation`. The CLI's `coval simulations metric-detail` does not return this field.

Attempt to fetch it via the API:

```bash
curl -s "https://api.coval.dev/v1/simulations/{simulation_output_id}/outputs/{simulation_output_id}/metrics/{metric_output_id}" \
  -H "X-API-Key: $COVAL_API_KEY"
```

If the response includes `result.llm.answer_explanation`, use it. If not, proceed without the LLM explanation — the transcript and reviewer notes are sufficient.

**Important:** Get the API key from the CLI config:
```bash
coval config get api-key
```
If that fails, check `~/.config/coval/config.json` or the `COVAL_API_KEY` environment variable.

### Step 3: Build the analysis dataset

For each annotation, you should have:

| Field | Source |
|-------|--------|
| `simulation_id` | annotation.simulation_output_id |
| `human_label` | annotation.ground_truth_float_value OR ground_truth_string_value |
| `machine_label` | simulation metric output value |
| `reviewer_notes` | annotation.reviewer_notes |
| `transcript` | simulation.transcript |
| `llm_explanation` | metric output result.llm.answer_explanation (if available) |
| `agrees` | computed in Phase 2 |

---

## Phase 2: Calculate Agreement

### Agreement rules by metric type

#### Binary (`METRIC_LLM_BINARY`)

Machine output is typically `1.0` (pass) or `0.0` (fail). Human ground truth is the same.

```
agrees = (human_label == machine_label)
```

**Tolerance: 0** — exact match only.

#### Categorical (`METRIC_CATEGORICAL`)

Machine and human both produce a category string.

```
agrees = (human_label == machine_label)
```

**Tolerance: 0** — exact match only.

#### Numerical (`METRIC_NUMERICAL_LLM_JUDGE`)

Machine and human both produce a float in the range `[min_value, max_value]`.

```
tolerance = 0  # exact match by default
agrees = (abs(human_label - machine_label) <= tolerance)
```

**Tolerance: 0** — exact match. If the agreement rate is very low with exact match, note this in the report and suggest the user may want to consider a wider tolerance. Do NOT automatically widen it.

### Compute and present the agreement report

Present results in this format:

> ## Agreement Report
>
> **Metric:** {metric_name} ({metric_type})
> **Total completed annotations:** {N}
> **Agreement rate:** {agree_count}/{N} ({percentage}%)
>
> ### Breakdown
> | | Count | % |
> |---|---|---|
> | Agree | {agree_count} | {agree_pct}% |
> | Disagree | {disagree_count} | {disagree_pct}% |
>
> {For numerical metrics only:}
> **Mean absolute error:** {mae}
> **Score range:** {min_value}–{max_value}

---

## Phase 3: Analyze Patterns

This is the most critical phase. You are acting as a metric prompt engineer analyzing real disagreements to improve accuracy.

### Step 1: Analyze disagreements

For each annotation where `agrees == false`:

1. Read the **transcript** carefully — understand the full conversation
2. Read the **reviewer notes** — understand WHY the human disagreed with the machine
3. Read the **LLM explanation** (if available) — understand the machine's reasoning
4. Determine who was more likely correct and why the machine erred

Look for patterns across disagreements:
- **Systematic bias**: Does the machine consistently score too high or too low?
- **Edge cases**: Are there conversation patterns the prompt doesn't account for?
- **Ambiguity**: Is the prompt vague about certain scenarios?
- **Missing context**: Does the prompt fail to instruct the LLM about important nuances?
- **Misinterpretation**: Does the LLM misunderstand what the prompt is asking?

### Step 2: Analyze agreements

For each annotation where `agrees == true`:

1. Read a sample of **reviewer notes** (if any) — understand what the metric handles well
2. Identify what the current prompt does correctly — these strengths must be preserved

### Step 3: Synthesize findings

Present a structured analysis:

> ## Analysis
>
> ### What the metric gets right
> - {bullet points from agreement analysis}
>
> ### Disagreement patterns
> - **Pattern 1:** {description} (seen in {N} annotations)
>   - Example: Simulation {sim_id} — Human: {value}, Machine: {value}
>   - Reviewer note: "{note}"
>   - Root cause: {why the machine got this wrong}
>
> - **Pattern 2:** ...
>
> ### Key insights from reviewer notes
> - {synthesized themes from reviewer feedback}

---

## Phase 3.5: Choose Resolution Path

After presenting the analysis, ask the user how they want to resolve the disagreements. The machine may be wrong (prompt needs fixing), OR the human labels may be wrong (labels need correcting), OR both.

Present the disagreements as a numbered list:

> ## Disagreements
>
> | # | Simulation | Human Label | Machine Label | Reviewer Note |
> |---|-----------|-------------|---------------|---------------|
> | 1 | {sim_id} | {human} | {machine} | {note or "—"} |
> | 2 | {sim_id} | {human} | {machine} | {note or "—"} |
> | ... | | | | |
>
> **How would you like to resolve these?**
> 1. **Update the metric prompt** — fix the prompt so the machine aligns with the human labels
> 2. **Update human labels** — correct the human labels to align with the machine scores
> 3. **Both** — update some labels and fix the prompt
>
> If choosing option 2 or 3, specify which disagreements to relabel (e.g., "update labels for #1, #3, #5" or "all").

### Handling label updates

If the user chooses to update labels (option 2 or 3):

1. For each annotation the user selects, confirm the new ground-truth value:
   > "Annotation #{n} (Simulation {sim_id}): Current human label is `{human_value}`. Update to `{machine_value}` (the machine score)? Or enter a different value."

2. After confirmation, update each annotation:
   ```bash
   coval review-annotations update <annotation_id> \
     --ground-truth-float <new_value> \
     --notes "Label corrected during metric improvement review. Previous value: {old_value}"
   ```
   For string-based metrics, use `--ground-truth-string` instead of `--ground-truth-float`.

3. After all label updates, **recalculate the agreement rate** with the corrected labels and present the updated report.

4. If the user chose option 2 (labels only), skip to the end — no prompt changes needed.
5. If the user chose option 3 (both), continue to Phase 4 with the remaining disagreements that were NOT resolved by label updates.

### Handling prompt updates

If the user chooses option 1 or 3, proceed to Phase 4.

---

## Phase 4: Propose Improved Prompt

### Step 1: Draft the improved prompt

Based on the analysis in Phase 3, draft an improved version of the metric prompt that:

1. **Preserves what works** — keep language that leads to correct evaluations
2. **Addresses disagreement patterns** — add explicit instructions for edge cases
3. **Incorporates reviewer feedback** — use the language and reasoning from reviewer notes
4. **Remains clear and concise** — avoid bloating the prompt with excessive detail
5. **Maintains the same evaluation format** — the metric type and output format must not change

### Step 2: Present the proposal

Show the current and proposed prompts side by side:

> ## Proposed Prompt Update
>
> ### Current prompt
> ```
> {current_prompt}
> ```
>
> ### Proposed prompt
> ```
> {new_prompt}
> ```
>
> ### Changes explained
> - {bullet point explaining each significant change and which disagreement pattern it addresses}
>
> **Would you like to apply this prompt update?** (yes/no)

### Step 3: Handle user response

- **If yes** → proceed to Phase 5
- **If no** → ask what they'd like to change. Iterate on the prompt until they approve or decide to stop.
- **If they want to edit manually** — that's fine too. The analysis is the primary value.

---

## Phase 5: Update the Metric

Only after the user explicitly approves the prompt.

```bash
coval metrics update <metric_id> --prompt "<approved_prompt>"
```

Verify the update:

```bash
coval metrics get <metric_id> --format json
```

Confirm the prompt matches what was approved.

> Metric prompt updated successfully. You can re-run simulations and create a new review project to validate the improvement.

---

## Reference

### CLI Commands Used

| Command | Purpose |
|---------|---------|
| `coval metrics get <id>` | Fetch metric definition (name, type, prompt) |
| `coval review-projects get <id>` | Fetch project details |
| `coval review-annotations list --filter '...'` | List completed annotations |
| `coval simulations metrics <sim_id>` | Get machine scores for a simulation |
| `coval simulations get <sim_id>` | Get transcript |
| `coval metrics update <id> --prompt "..."` | Update metric prompt (after approval) |

### Supported Metric Types

| Type | Machine Output | Human Output | Agreement |
|------|---------------|--------------|-----------|
| `METRIC_LLM_BINARY` | `1.0` (pass) / `0.0` (fail) | Same | Exact match |
| `METRIC_CATEGORICAL` | Category string | Same | Exact match |
| `METRIC_NUMERICAL_LLM_JUDGE` | Float in [min, max] | Same | Exact match (tolerance = 0) |

### Data Flow

```
Review Project
  └─ Annotations (filtered by metric_id, completion_status=COMPLETED)
       ├─ ground_truth_float_value / ground_truth_string_value  ← human label
       ├─ reviewer_notes                                         ← human reasoning
       └─ simulation_output_id
            ├─ coval simulations metrics → value                 ← machine label
            ├─ coval simulations get → transcript                ← conversation
            └─ API: result.llm.answer_explanation                ← machine reasoning
```