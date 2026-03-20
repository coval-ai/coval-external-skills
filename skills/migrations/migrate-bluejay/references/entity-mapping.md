# Entity Mapping: Bluejay → Coval

Field-by-field mapping for each entity pair.

## Agent → Agent

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `name` | `display_name` | Direct. Prefix with `[folder_name]` if agent has folder |
| `mode` | `model_type` | `VOICE` → `MODEL_TYPE_VOICE`, `TEXT` → `MODEL_TYPE_TEXT` |
| `system_prompt` | `prompt` (part 1) | Prepend to prompt content |
| Latest `prompt_text` | `prompt` (part 2) | Append after system_prompt |
| `goals` | `prompt` (part 3) | Append as numbered list: `\n\nGoals:\n1. goal1\n2. goal2` |
| `knowledge_base` / latest `kb_text` | `metadata.knowledge_base` | Store as metadata string |
| `agent_id` | `metadata.bluejay_original_id` | For traceability |
| `connection_type` | `metadata.bluejay_connection_type` | Informational only |
| `phone_number` | `metadata.bluejay_phone_number` | Informational only |
| `type` | `metadata.bluejay_call_direction` | `INBOUND`/`OUTBOUND` |
| `external_agent_id` | `metadata.bluejay_external_id` | Informational only |

**Prompt assembly order:**
```
<system_prompt>

<latest_prompt_text>

Goals:
1. <goal_1>
2. <goal_2>
```

## Digital Human (voice/behavior) → Persona

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `name` | `name` | Direct |
| `gender` + `accent` + `language` | `voice_name` | Interactive mapping — ask user |
| `language` | `language_code` | See language code table below |
| `role_description` + `traits` | `persona_prompt` | Combine into prompt text |
| `background_noise` | `background_sound` | See noise mapping table below |
| `speaks_first_config` | `conversation_initiation` | `true` → `speak_first`, `false`/absent → `wait_for_user` |
| `verbosity` | `persona_prompt` (append) | Append: "Verbosity level: <level>" |
| `fluency` | `persona_prompt` (append) | Append: "Fluency level: <level>" |
| `voice_speed` | `persona_prompt` (append) | Append: "Speaking speed: <speed>" |
| `creativity` | `persona_prompt` (append) | Append: "Creativity/temperature: <value>" |

### Language Code Mapping

| Bluejay `language` | Coval `language_code` |
|--------------------|-----------------------|
| `en` | `en-US` |
| `es` | `es-ES` |
| `pt` | `pt-BR` |
| `ja` | `ja-JP` |
| `tr` | `tr-TR` |
| `hi` | `hi-IN` |
| `ar` | `ar-SA` |
| `ru` | `ru-RU` |
| `zh` | `zh-CN` |
| `fr` | `fr-FR` |
| `de` | `de-DE` |
| `vi` | `vi-VN` |
| `yue` | `zh-HK` |
| `ml` | `ml-IN` |

### Background Noise Mapping

| Bluejay `background_noise` | Coval `background_sound` |
|---------------------------|--------------------------|
| `none` | `off` |
| `office` | `office` |
| `talking` | `crowd` |
| `traffic` | `street-with-sirens` |
| `cafe` | `cafe` |
| `park` | `playground` |
| `tv` | `lounge` |

### Persona Prompt Assembly

```
<role_description>

Traits: <traits>

Behavioral settings:
- Verbosity: <verbosity>
- Fluency: <fluency>
- Speaking speed: <voice_speed>
- Creativity: <creativity>

<hangup_instructions if present>
```

## Digital Human (intent/criteria) → Test Case

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `intent` | `input_str` | Direct |
| `success_criteria` | `expected_behaviors` | Split by newline into array |
| `name` + `tag` | `description` | `"<name>: <tag>"` |
| — | `test_set_id` | From simulation → test set mapping |
| — | `input_type` | Default `SCENARIO`; `SCRIPT` if scripted_responses present |
| `scripted_responses` | `simulation_metadata_input.script_turns` | Array of turn strings |
| `expected_tool_calls` | `metric_input` | Store as metric input if present |
| `num_runs` | — | No direct equivalent (use iteration_count on run template) |

## Simulation → Test Set + Run Template

### Simulation → Test Set

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| Simulation name | `display_name` | Direct |
| `simulation_id` | `test_set_metadata.bluejay_original_id` | For traceability |
| — | `test_set_type` | `SCENARIO` |

### Simulation → Run Template

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| Simulation name | `display_name` | Append ` Template` |
| `agent_id` | `agent_id` | Lookup from agent mapping |
| First digital human | `persona_id` | Lookup from persona mapping |
| — | `test_set_id` | From test set mapping |
| Agent's metrics | `metric_ids` | From metric mapping |
| — | `iteration_count` | Default 1 |
| — | `concurrency` | Default 5 |

## Community → Test Set

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `title` | `display_name` | Direct |
| `description` | `description` | Direct |
| `id` | `test_set_metadata.bluejay_original_id` | For traceability |
| — | `test_set_type` | `SCENARIO` |

Note: Community's `digital_human_ids` → create test cases under this test set.

## Custom Metric → Metric

See [metric-type-mapping.md](metric-type-mapping.md) for type-specific details.

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `name` | `metric_name` | Direct |
| `description` | `description` | Direct |
| `response_type` | `metric_type` | See metric type mapping |
| `scoring_guidance` | `prompt` | Direct (may need formatting) |
| `min_value` | `min_value` | Direct (quantitative only) |
| `max_value` | `max_value` | Direct (quantitative only) |
| `enum_options` | `categories` | Direct (enum only) |
| `eval_route` | — | `AUDIO` → use audio metric variants |

## Customer Persona → Persona

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `name` | `name` | Direct |
| `name` + `description` + `goal` | `persona_prompt` | Combine into structured prompt |
| — | `voice_name` | Ask user (default `aria`) |
| — | `language_code` | Default `en-US` |

### Persona Prompt Assembly

```
Name: <name>
Description: <description>
Goal: <goal>
```

## Schedule → Scheduled Run

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| Simulation name | `display_name` | Append ` Schedule` |
| `simulation_id` | `run_template_id` | Lookup from run template mapping |
| Schedule config | `schedule_expression` | See conversion table below |
| — | `enabled` | Always `false` (safety) |

### Schedule Expression Conversion

| Bluejay Format | Coval Format |
|----------------|--------------|
| `every_n_minutes`, interval=N | `rate(N minutes)` |
| `every_n_hours`, interval=N | `rate(N hours)` |
| `daily`, time=HH:MM | `cron(MM HH ? * * *)` |
| `weekly`, day=DAY, time=HH:MM | `cron(MM HH ? * DAY *)` — DAY in uppercase 3-letter |
| `monthly`, day=D, time=HH:MM | `cron(MM HH D * ? *)` |
| `cron`, expression=EXPR | `cron(EXPR)` — wrap in `cron()` if not already |

## Folder → Naming Prefix

| Bluejay Field | Coval Field | Transformation |
|---------------|-------------|----------------|
| `name` | Agent `display_name` prefix | `"[FolderName] AgentName"` |

No Coval folder entity exists. Folder names are encoded into `display_name` prefixes.
