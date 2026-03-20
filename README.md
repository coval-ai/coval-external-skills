# Coval External Skills

Agent Skills for AI evaluation workflows with Coval. Follows the [Agent Skills](https://agentskills.io) open standard.

## Overview

This repository contains reusable skills for interacting with Coval's evaluation platform. Skills are organized by resource type and can be integrated into LLM-based agents and automation workflows.

## Skills

| Category | Description |
|----------|-------------|
| [Runs](./skills/runs/) | Launch and monitor evaluation runs |
| [Simulations](./skills/simulations/) | Analyze results and download audio |
| [Agents](./skills/agents/) | Create, configure, and manage AI agents |
| [Personas](./skills/personas/) | Define simulation personas for testing |
| [Test Cases](./skills/test-cases/) | Build and organize evaluation test cases (includes HuggingFace import) |
| [Metrics](./skills/metrics/) | Configure evaluation metrics and scoring |
| [Migrations](./skills/migrations/) | Migrate from other testing platforms |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/coval-ai/coval-external-skills.git

# Navigate to a skill category
cd coval-external-skills/skills/agents
```

## Skill Structure

Each skill is a directory with `SKILL.md` as the entrypoint:

```
skills/<category>/<skill-name>/
├── SKILL.md           # Main instructions (required)
├── examples/          # Usage examples
└── scripts/           # Utility scripts (optional)
```

Skills use YAML frontmatter for configuration:

```yaml
---
name: skill-name
description: What this skill does and when to use it
argument-hint: "[expected-arguments]"
---
```

## Requirements

- Coval CLI (`brew install coval-ai/tap/coval`)
- Coval API access ([coval.dev](https://coval.dev))
- API key with appropriate permissions

## API Reference

**Base URL:** `https://api.coval.dev/v1`

```bash
# List available OpenAPI specs (no auth required)
GET https://api.coval.dev/v1/openapi

# Fetch specific spec (YAML default, use Accept: application/json for JSON)
GET https://api.coval.dev/v1/openapi/{spec_name}
```

Always fetch the latest spec before building integrations.

## Documentation

See [docs.coval.dev](https://docs.coval.dev) for full API documentation.

## License

MIT License - see [LICENSE](./LICENSE) for details.
