# Bluejay API Reference

## Base URL

```
https://api.getbluejay.ai
```

## Authentication

All requests require the `X-API-Key` header:

```bash
curl -H "X-API-Key: <BLUEJAY_API_KEY>" "https://api.getbluejay.ai/v1/..."
```

## Pagination

Bluejay uses page-based pagination:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | 1-based page number |
| `page_size` | integer | 50 | Items per page (max 100) |

Response includes:

```json
{
  "total_count": 42,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "items_in_page": 42
}
```

## Endpoints

### Agents

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/all-agents` | List all agents |
| `GET` | `/v1/agents/{agent_id}` | Get agent by ID |
| `GET` | `/v1/agent-by-external-id/{external_id}` | Get by external ID |

**Agent fields:**

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | integer | Unique ID |
| `name` | string | Agent name |
| `system_prompt` | string | System prompt text |
| `knowledge_base` | string | Knowledge base content |
| `goals` | string[] | Agent goals |
| `phone_number` | string | Phone number |
| `type` | enum | `INBOUND` or `OUTBOUND` |
| `connection_type` | enum | `SMS`, `HTTP_WEBHOOK`, `PHONE`, `SIP`, `WEBSOCKET`, `LIVEKIT`, `PIPECAT` |
| `mode` | enum | `VOICE` or `TEXT` |
| `folder` | string | Folder name |
| `external_agent_id` | string | External identifier |
| `redact_pii` | boolean | PII redaction enabled |

### Prompts (per agent, versioned)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/agents/{agent_id}/prompts/versions` | List prompt versions |
| `GET` | `/v1/agents/{agent_id}/prompts/versions/{version}` | Get specific version |
| `GET` | `/v1/agents/{agent_id}/prompts?label=latest` | Get by label |

**Prompt fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Prompt ID |
| `prompt_text` | string | The prompt content |
| `version` | integer | Version number |
| `commit_message` | string | Version description |
| `labels` | string[] | Version labels (e.g., `latest`, `production`) |
| `metadata` | object | Custom metadata |
| `agent_id` | integer | Parent agent |

To get the latest prompt: `GET /v1/agents/{agent_id}/prompts?label=latest`

### Knowledge Bases (per agent, versioned)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/agents/{agent_id}/knowledge-bases/versions` | List KB versions |
| `GET` | `/v1/agents/{agent_id}/knowledge-bases/versions/{version}` | Get specific version |
| `GET` | `/v1/agents/{agent_id}/knowledge-bases?label=latest` | Get by label |

**Knowledge Base fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | KB ID |
| `kb_text` | string | Knowledge base content |
| `version` | integer | Version number |
| `commit_message` | string | Version description |
| `labels` | string[] | Version labels |
| `metadata` | object | Custom metadata |
| `agent_id` | integer | Parent agent |

### Simulations

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/get-all-simulations` | List all simulations |
| `GET` | `/v1/simulation/{simulation_id}` | Get simulation by ID |
| `GET` | `/v1/get-simulations-by-agent/{agent_id}` | List by agent |

**Simulation fields:**

| Field | Type | Description |
|-------|------|-------------|
| `simulation_id` | string | Unique ID |
| `agent_id` | integer | Associated agent |
| `name` | string | Simulation name |
| `digital_human_ids` | string[] | Associated digital humans |

### Digital Humans

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/digital-human/{digital_human_id}` | Get by ID |
| `GET` | `/v1/digital-humans-by-simulation/{simulation_id}` | List by simulation |

**Digital Human fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | — | Unique ID |
| `intent` | string | yes | Purpose/scenario description |
| `success_criteria` | string | yes | How to judge success |
| `phone_number` | string | yes | Phone number |
| `name` | string | no | Display name |
| `tag` | string | no | Category tag |
| `simulation_ids` | int[] | no | Associated simulations |
| `language` | enum | no | `en`, `es`, `pt`, `ja`, `tr`, `hi`, `ar`, `ru`, `zh`, `ml`, `fr`, `yue`, `vi`, `de` |
| `accent` | enum | no | `multilingual`, `american`, `southern`, `italian`, `indian`, `british`, `australian`, `mexican`, `spanish`, `portuguese`, `french`, `turkish`, `japanese`, `hindi`, `arabic`, `russian`, `chinese`, `german` |
| `gender` | enum | no | `male`, `female` |
| `background_noise` | enum | no | `none`, `office`, `talking`, `traffic`, `cafe`, `park`, `tv` |
| `voice_speed` | enum | no | `slowest`, `slow`, `normal`, `fast`, `fastest` |
| `audio_quality` | enum | no | `high`, `medium`, `low`, `horrible` |
| `fluency` | enum | no | `beginner`, `intermediate`, `native` |
| `verbosity` | enum | no | `low`, `medium`, `high` |
| `creativity` | number | no | 0–2 (default 0.7) |
| `role_description` | string | no | Character description |
| `traits` | string | no | Personality traits |
| `interruptions` | object | no | Interruption behavior |
| `scripted_responses` | array | no | Scripted conversation turns |
| `speaks_first_config` | object | no | Whether persona speaks first |
| `hangup_phrases` | array | no | Phrases that trigger hangup |
| `hangup_instructions` | string | no | Hangup behavior rules |
| `expected_tool_calls` | array | no | Expected tool call invocations |
| `num_runs` | integer | no | Number of runs per sim |

### Custom Metrics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/custom-metrics` | List all (paginated) |
| `GET` | `/v1/custom-metric/{metric_id}` | Get by ID |

**Query parameters:** `page`, `page_size`, `agent_id` (optional filter)

**Custom Metric fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | — | Metric ID |
| `name` | string | yes | Metric name |
| `description` | string | yes | What it measures |
| `response_type` | enum | yes | `pass_fail`, `yes_no`, `qualitative`, `quantitative`, `json`, `enum` |
| `scoring_guidance` | string | no | Grading instructions |
| `agent_ids` | int[] | no | Associated agents |
| `min_value` | number | no | For quantitative |
| `max_value` | number | no | For quantitative |
| `enum_options` | string[] | no | For enum type |
| `tags` | string[] | no | Category tags |
| `eval_route` | enum | no | `AUDIO`, `TEXT`, `AUTO` (default `AUTO`) |
| `model` | string | no | LLM model override |
| `temperature` | number | no | LLM temperature |
| `allow_not_applicable` | boolean | no | Allow N/A results |

### Communities

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/communities` | List all communities |
| `GET` | `/v1/community/{community_id}` | Get by ID |

**Community fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Community ID |
| `title` | string | Display name |
| `description` | string | Description |
| `digital_human_ids` | int[] | Member digital humans |
| `created_at` | datetime | Creation timestamp |

### Customer Personas

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/customer-persona/{persona_id}` | Get by ID |
| `GET` | `/v1/customer-personas-by-agent/{agent_id}` | List by agent |

**Customer Persona fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Persona ID |
| `name` | string | Persona name |
| `description` | string | Background description |
| `goal` | string | What the persona wants |
| `agent_id` | integer | Associated agent |
| `created_at` | datetime | Creation timestamp |

### Schedules

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/update-schedule/{schedule_id}` | Get schedule (note: GET despite path name) |

**Schedule fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Schedule ID |
| `simulation_id` | string | Associated simulation |
| `cron_expression` | string | Cron schedule |
| `enabled` | boolean | Active state |

**Schedule frequency types:**

| Type | Fields |
|------|--------|
| `every_n_minutes` | `interval` (1–59) |
| `every_n_hours` | `interval` (1–23) |
| `daily` | `time` (HH:MM) |
| `weekly` | `day_of_week`, `time` |
| `monthly` | `day_of_month` (1–31), `time` |
| `cron` | `expression` (cron string) |

### Folders

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/all-folders` | List all folders |
| `GET` | `/v1/get-agents-by-folder/{folder_id}` | List agents in folder |

**Folder fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Folder ID |
| `name` | string | Folder name |
