# Coval External Skills

Agent Skills for AI evaluation workflows with Coval. Follows the [Agent Skills](https://agentskills.io) open standard.

## Overview

This repository contains reusable skills for interacting with Coval's evaluation platform. Start with a product question: what must your agent get right, and what evidence would show it? The starter collection below guides a small first evaluation, failure discovery, metric calibration and regression checks. Resource-specific and specialist skills remain available for targeted work.

## Recommended starter collection

Install the collection, then ask your coding agent:

> Use `coval-eval-start` to help me evaluate my agent with Coval. Reuse what I
> already have, propose a small execution budget, and distinguish working setup
> from evidence that my agent performs well.

| Skill | When it helps | What you get |
|-------|---------------|--------------|
| [coval-eval-start](skills/evaluation/coval-eval-start/SKILL.md) | You want help choosing the next step | A route based on existing evidence and your product decision |
| [onboard](skills/onboarding/onboard/SKILL.md) | No usable evaluation yet | A small first run with inspected results |
| [coval-discover-failures](skills/evaluation/coval-discover-failures/SKILL.md) | You have conversations or recordings | Failure hypotheses grounded in transcript, audio and trace evidence |
| [build-test-suite](skills/test-cases/build-test-suite/SKILL.md) | You know the requirement or coverage gap | Realistic cases with separate expectations and provenance |
| [configure-metrics](skills/metrics/configure-metrics/SKILL.md) | You know what needs measuring | A suitable metric and tested, provisional criterion |
| [quick-eval](skills/runs/quick-eval/SKILL.md) | You want to run selected cases | Explicit execution bounds and a complete result audit |
| [coval-calibrate-metric](skills/evaluation/coval-calibrate-metric/SKILL.md) | You need to trust a judge's scores | Human-label error rates, uncertainty and held-out validation |
| [coval-compare-runs](skills/evaluation/coval-compare-runs/SKILL.md) | You changed the agent | Matched before/after evidence and visible regressions |
| [coval-eval-audit](skills/evaluation/coval-eval-audit/SKILL.md) | You already have an eval setup | Prioritized findings about what its results can support |

A first voice run starts small: one case, one persona, one iteration, concurrency
one. The agent presents the concrete plan before spending, uses an agreed session
budget, and counts reruns and base + mutation variants. These are workflow controls,
not server-side spending limits. An audit or planning request does not authorize
calls. A few successful conversations prove a smoke test, not production quality.

The skills work with voice and chat; they require recordings for acoustic claims
and trace/tool evidence for actual side effects. Human calibration requires real
human labels. Without them, the output is a review-ready plan, not fabricated
validation. Existing Coval Human Review is preferred over building another UI.

## Skills

| Category | Description |
|----------|-------------|
| [Onboarding](./skills/onboarding/) | Interactive guided setup for first evaluation (personas, test cases, metrics, launch) |
| [Runs](./skills/runs/) | Launch and monitor evaluation runs |
| [Simulations](./skills/simulations/) | Analyze results and download audio |
| [Reports](./skills/reports/) | Analyze multi-run reports and turn grouped results into action plans |
| [Agents](./skills/agents/) | Create, configure, and manage AI agents |
| [Personas](./skills/personas/) | Define simulation personas for testing |
| [Test Cases](./skills/test-cases/) | Build and organize evaluation test cases (includes HuggingFace import) |
| [Metrics](./skills/metrics/) | Configure evaluation metrics and scoring |
| [Traces](./skills/traces/) | Configure, enrich, measure, and debug OpenTelemetry traces |
| [Migrations](./skills/migrations/) | Migrate from other testing platforms |
| [Sofia](./skills/sofia/) | Delegate read-only Coval FDE analysis to Sofia from an external coding agent |

## Quick Start

```bash
# Install Coval skills into your chosen Agent Skills-compatible coding agent
npx skills add coval-ai/coval-external-skills --skill coval-eval-start onboard coval-discover-failures build-test-suite configure-metrics quick-eval coval-calibrate-metric coval-compare-runs coval-eval-audit

# Install the Coval CLI
brew install coval-ai/tap/coval

# Authenticate
coval login

# Then ask your coding agent to use coval-eval-start
```

To install only the recommended starter collection, select the nine skills above
in the installer, or use its explicit skill selector:

```bash
npx skills add coval-ai/coval-external-skills --skill coval-eval-start onboard coval-discover-failures build-test-suite configure-metrics quick-eval coval-calibrate-metric coval-compare-runs coval-eval-audit
```

Choose the target agent and project/global installation scope in the installer.
Skill names are instructions to your coding agent, not terminal commands. You can
install an individual skill; router handoffs require the selected destination
skill to be installed. Python 3.10+ is needed only for the optional local planner,
read-only evidence fetcher and calibration calculator. No Coval internal tools,
AWS access or database credentials are required.

Use `coval --agent agent doctor` and `coval --agent agent manifest` to check the
installed CLI. Verify the intended org/workspace separately: doctor does not
identify your tenant. Current schemas live at the public `/v1/openapi` endpoint.

### Manual Installation

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

## Validation and maintenance

Maintainers can run the local behavior tests with:

```bash
python3 -m unittest discover -s tests -v
```

These check execution arithmetic, pagination/scoping and calibration edge cases.
[The behavioral scenarios](tests/behavioral-scenarios.md) exercise judgment and
negative paths. They supplement actual customer-API voice testing; neither a
Markdown validator nor a synthetic fixture certifies an agent or LLM judge.

## Acknowledgments

The maturity-aware evaluation workflow was informed by
[Hamel Husain and Shreya Shankar's evals-skills](https://github.com/ai-evals-course/evals-skills).
Coval's collection uses its own resources, recordings, review projects, metric
outputs and bounded voice execution. It does not require their plugin.

## License

MIT License - see [LICENSE](./LICENSE) for details.
