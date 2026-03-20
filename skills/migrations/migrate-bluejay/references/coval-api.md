# Coval API Reference

## Base URL

```
https://api.coval.dev
```

## Authentication

All requests require the `X-API-Key` header:

```bash
curl -H "X-API-Key: <COVAL_API_KEY>" "https://api.coval.dev/v1/..."
```

## Pagination

Coval uses token-based pagination:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_size` | integer | 50 | Items per page (1–100) |
| `page_token` | string | — | Opaque token for next page |
| `order_by` | string | `-create_time` | Sort order |
| `filter` | string | — | Filter expression |

Response includes:

```json
{
  "<resource_type>": [...],
  "next_page_token": "abc123"
}
```

`next_page_token` is null or omitted on the last page.

## Error Response Format

```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Human-readable message",
    "details": [{ "field": "field_name", "description": "..." }]
  }
}
```

| Status | Meaning |
|--------|---------|
| `201` | Created |
| `400` | Bad request (validation error) |
| `401` | Invalid API key |
| `404` | Resource not found |
| `409` | Conflict (duplicate name/slug) |
| `429` | Rate limited |
| `500` | Server error |

## Endpoints

### Agents

**Create:** `POST /v1/agents`

```json
{
  "display_name": "string (1-200 chars, required)",
  "model_type": "MODEL_TYPE_VOICE | MODEL_TYPE_TEXT (required)",
  "prompt": "string (agent instructions)",
  "metadata": {}
}
```

**List:** `GET /v1/agents`

Query: `page_size`, `page_token`, `order_by`, `filter`

Filter supports: `model_type`, `display_name`, `create_time`, `update_time`

**Get:** `GET /v1/agents/{agent_id}`

ID format: 22-character alphanumeric (ShortUUID)

### Personas

**Create:** `POST /v1/personas`

```json
{
  "name": "string (1-200 chars, required)",
  "voice_name": "string (required, e.g. 'aria')",
  "language_code": "string (BCP-47, required, e.g. 'en-US')",
  "persona_prompt": "string (behavior instructions)",
  "background_sound": "off | office | lounge | crowd | airport | bus | cafe | ...",
  "wait_seconds": 0.1-2.0,
  "conversation_initiation": "speak_first | wait_for_user",
  "metadata": {}
}
```

**List:** `GET /v1/personas`

**Get:** `GET /v1/personas/{persona_id}`

ID format: 22-character alphanumeric

**Voices:** `GET /v1/personas/voices`

```json
{
  "voices": [
    {
      "voice_name": "aria",
      "supported_languages": ["en-US", "en-GB", "es-ES", "fr-FR"]
    }
  ]
}
```

Available background sounds: `off`, `office`, `lounge`, `crowd`, `airport`, `bus`, `playground`, `doorbell`, `train-arrival`, `portable-air-conditioner`, `skatepark`, `small-dog-bark`, `cafe`, `ferry-and-announcement`, `heavy-rain`, `moderate-wind`, `newborn-baby-crying`, `office-with-alarm`, `street-with-sirens`, `construction-work`

### Test Sets

**Create:** `POST /v1/test-sets`

```json
{
  "display_name": "string (1-100 chars, required)",
  "slug": "string (auto-generated if omitted)",
  "description": "string",
  "test_set_type": "DEFAULT | SCENARIO | TRANSCRIPT | WORKFLOW",
  "test_set_metadata": {},
  "parameters": {}
}
```

**List:** `GET /v1/test-sets`

Filter supports: `test_set_type`

**Get:** `GET /v1/test-sets/{test_set_id}`

ID format: 8-character alphanumeric

### Test Cases

**Create:** `POST /v1/test-cases`

```json
{
  "test_set_id": "string (8-char, required)",
  "input_str": "string (required)",
  "expected_behaviors": ["string array"],
  "description": "string",
  "input_type": "SCENARIO | TRANSCRIPT | IVR | AUDIO | MANUAL | SCRIPT",
  "simulation_metadata_input": {
    "script_turns": ["turn 1", "turn 2"]
  },
  "metric_input": {},
  "user_notes": "string",
  "metadata": {}
}
```

**List:** `GET /v1/test-cases`

**Get:** `GET /v1/test-cases/{test_case_id}`

ID format: 22-character alphanumeric

Note: `expected_output_str` is deprecated. Use `expected_behaviors` (string array).

### Metrics

**Create:** `POST /v1/metrics`

Common fields:

```json
{
  "metric_name": "string (required)",
  "description": "string",
  "metric_type": "string (required, see types below)",
  "prompt": "string (grading instructions)",
  "metadata": {}
}
```

**Type-specific fields:**

| Metric Type | Additional Required Fields |
|-------------|---------------------------|
| `METRIC_LLM_BINARY` | `prompt` |
| `METRIC_CATEGORICAL` | `prompt`, `categories` (string[]) |
| `METRIC_NUMERICAL_LLM_JUDGE` | `prompt`, `min_value` (number), `max_value` (number) |
| `METRIC_AUDIO_LLM_BINARY` | `prompt` |
| `METRIC_AUDIO_LLM_CATEGORICAL` | `prompt`, `categories` (string[]) |
| `METRIC_AUDIO_LLM_NUMERICAL` | `prompt`, `min_value`, `max_value` |
| `METRIC_TOOLCALL` | `prompt` |
| `METRIC_METADATA_FIELD` | `metadata_field_type`, `metadata_field_key` |
| `METRIC_TRANSCRIPT_REGEX` | `regex_pattern` |
| `METRIC_PAUSE_ANALYSIS` | `min_pause_duration_seconds` |

**List:** `GET /v1/metrics`

Query: `include_builtin` (boolean), `filter`, `page_size`, `page_token`

**Get:** `GET /v1/metrics/{metric_id}`

ID format: 22-character alphanumeric

### Run Templates

**Create:** `POST /v1/run-templates`

```json
{
  "display_name": "string (1-200 chars, required)",
  "agent_id": "string (22-char, required)",
  "persona_id": "string (22-char, required)",
  "test_set_id": "string (8-char, required)",
  "description": "string",
  "metric_ids": ["22-char IDs"],
  "mutation_ids": ["26-char ULIDs"],
  "iteration_count": 1,
  "concurrency": 1,
  "sub_sample_size": 0,
  "sub_sample_seed": 0,
  "metadata": {}
}
```

**List:** `GET /v1/run-templates`

**Get:** `GET /v1/run-templates/{run_template_id}`

ID format: 22-character alphanumeric

### Scheduled Runs

**Create:** `POST /v1/scheduled-runs`

```json
{
  "display_name": "string (1-200 chars, required)",
  "run_template_id": "string (22-char, required)",
  "schedule_expression": "string (required)",
  "schedule_timezone": "string (IANA, default 'UTC')",
  "enabled": false,
  "metadata": {}
}
```

**Schedule expression formats:**

Rate:
```
rate(15 minutes)
rate(1 hour)
rate(1 day)
```

Cron:
```
cron(0 9 ? * MON-FRI *)     # 9am weekdays
cron(0 2 ? * * *)           # 2am daily
cron(0 0 1 * ? *)           # Midnight 1st of month
```

**List:** `GET /v1/scheduled-runs`

Query: `enabled` (boolean), `template_id` (22-char)

**Get:** `GET /v1/scheduled-runs/{scheduled_run_id}`

ID format: 22-character alphanumeric
