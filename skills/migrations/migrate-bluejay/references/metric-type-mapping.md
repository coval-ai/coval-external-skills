# Metric Type Mapping: Bluejay → Coval

## Overview

Bluejay uses `response_type` to categorize metrics. Coval uses `metric_type` with type-specific fields. This document maps each Bluejay type to its Coval equivalent.

## Quick Reference

| Bluejay `response_type` | Coval `metric_type` | Confidence | Notes |
|--------------------------|---------------------|------------|-------|
| `pass_fail` | `METRIC_LLM_BINARY` | High | Direct mapping |
| `yes_no` | `METRIC_LLM_BINARY` | High | Direct mapping |
| `qualitative` | `METRIC_CATEGORICAL` | Medium | Must ask user for categories |
| `quantitative` | `METRIC_NUMERICAL_LLM_JUDGE` | High | Needs min/max values |
| `enum` | `METRIC_CATEGORICAL` | High | Use enum_options as categories |
| `json` | `METRIC_LLM_BINARY` | Low | Best approximation — warn user |

### Audio Override

When Bluejay `eval_route == "AUDIO"`, use the audio variants instead:

| Bluejay `response_type` | Coval `metric_type` (audio) |
|--------------------------|----------------------------|
| `pass_fail` | `METRIC_AUDIO_LLM_BINARY` |
| `yes_no` | `METRIC_AUDIO_LLM_BINARY` |
| `qualitative` | `METRIC_AUDIO_LLM_CATEGORICAL` |
| `quantitative` | `METRIC_AUDIO_LLM_NUMERICAL` |
| `enum` | `METRIC_AUDIO_LLM_CATEGORICAL` |
| `json` | `METRIC_AUDIO_LLM_BINARY` |

## Detailed Mapping

### pass_fail → METRIC_LLM_BINARY

Direct mapping. Both represent binary pass/fail evaluation.

**Bluejay source fields:**
- `scoring_guidance` → `prompt`
- `description` → `description`

**Coval request:**
```json
{
  "metric_name": "<name>",
  "description": "<description>",
  "metric_type": "METRIC_LLM_BINARY",
  "prompt": "<scoring_guidance>"
}
```

### yes_no → METRIC_LLM_BINARY

Functionally identical to pass_fail. Map the same way.

**Coval request:**
```json
{
  "metric_name": "<name>",
  "description": "<description>",
  "metric_type": "METRIC_LLM_BINARY",
  "prompt": "<scoring_guidance>"
}
```

### qualitative → METRIC_CATEGORICAL

Qualitative free-text evaluation needs categories in Coval. **Must ask user** to define the category list since Bluejay doesn't enforce categories for this type.

**Interactive prompt:**
```
Metric "<name>" is qualitative in Bluejay.
Coval needs explicit categories for categorical metrics.

Description: <description>
Scoring guidance: <scoring_guidance>

What categories should this metric use?
Example: ["excellent", "good", "fair", "poor"]
```

**Coval request:**
```json
{
  "metric_name": "<name>",
  "description": "<description>",
  "metric_type": "METRIC_CATEGORICAL",
  "prompt": "<scoring_guidance>",
  "categories": ["<user_provided_categories>"]
}
```

### quantitative → METRIC_NUMERICAL_LLM_JUDGE

Numeric scoring. Use Bluejay's `min_value`/`max_value` if present; otherwise ask user.

**If min/max present in Bluejay:**
```json
{
  "metric_name": "<name>",
  "description": "<description>",
  "metric_type": "METRIC_NUMERICAL_LLM_JUDGE",
  "prompt": "<scoring_guidance>",
  "min_value": "<bluejay_min_value>",
  "max_value": "<bluejay_max_value>"
}
```

**If min/max NOT present, ask user:**
```
Metric "<name>" is quantitative but has no min/max defined in Bluejay.
Description: <description>

What should the scoring range be?
- min_value (default: 0):
- max_value (default: 10):
```

### enum → METRIC_CATEGORICAL

Direct mapping. Use Bluejay `enum_options` as Coval `categories`.

**Coval request:**
```json
{
  "metric_name": "<name>",
  "description": "<description>",
  "metric_type": "METRIC_CATEGORICAL",
  "prompt": "<scoring_guidance>",
  "categories": ["<enum_option_1>", "<enum_option_2>", "..."]
}
```

If `enum_options` is empty or missing, ask user for the category list.

### json → METRIC_LLM_BINARY (approximation)

Bluejay's JSON response type has no direct Coval equivalent. Map to `METRIC_LLM_BINARY` as the closest approximation.

**Always warn the user:**
```
Warning: Metric "<name>" uses JSON response type in Bluejay.
Coval doesn't have a JSON metric type. Mapping to METRIC_LLM_BINARY
as an approximation. You may need to adjust the prompt to work
as a binary (pass/fail) evaluation instead.
```

**Coval request:**
```json
{
  "metric_name": "<name>",
  "description": "<description> [Migrated from Bluejay JSON metric - may need prompt adjustment]",
  "metric_type": "METRIC_LLM_BINARY",
  "prompt": "<scoring_guidance>"
}
```

## Prompt Construction

For all metric types, build the `prompt` field from Bluejay's `scoring_guidance`:

1. If `scoring_guidance` is present and non-empty → use directly as `prompt`
2. If `scoring_guidance` is empty → construct from `description`:
   ```
   Evaluate the following based on: <description>
   ```
3. If both are empty → ask user to provide grading instructions

## Common Metadata

All migrated metrics include:

```json
{
  "metadata": {
    "bluejay_migration": true,
    "bluejay_original_id": "<metric_id>",
    "bluejay_response_type": "<original_response_type>",
    "bluejay_eval_route": "<eval_route>"
  }
}
```

## Edge Cases

1. **allow_not_applicable**: Bluejay supports `allow_not_applicable: true`. Coval doesn't have a direct equivalent. Note in metadata: `"bluejay_allow_na": true`
2. **model/temperature overrides**: Bluejay allows per-metric model and temperature. Coval doesn't support this per-metric. Note in metadata for user reference.
3. **Tags**: Bluejay metric tags have no Coval equivalent. Store in metadata: `"bluejay_tags": ["tag1", "tag2"]`
4. **Agent association**: Bluejay metrics are associated with specific agents via `agent_ids`. In Coval, metrics are global but referenced via run templates. No action needed during migration.
