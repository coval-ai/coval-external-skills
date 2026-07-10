---
name: consult-covi
description: Delegate a read-only Coval evaluation, simulation, monitoring, product-how-to, or troubleshooting subtask to Covi through the official Coval MCP tool. Use when the user needs Coval-specific FDE judgment, analysis of organization data, metric or test-set recommendations, or a diagnosis grounded in Coval runs and conversations.
---

# Consult Covi

Use `consult_covi` when Coval-specific expertise or the authenticated organization's data would improve the answer. Covi is a read-only specialist: it can use Coval knowledge plus the organization's runs, simulations, monitoring conversations, metrics, agents, personas, test sets, and dashboards.

This skill is optional guidance, not an installation prerequisite or a duplicate implementation. Prefer the official remote MCP connection at `https://mcp.coval.dev/mcp`; use the local stdio MCP server with a Coval API key only for service accounts or local development.

## When To Delegate

Delegate when the task needs one or more of:
- analysis of failed runs, simulations, or monitoring conversations
- recommendations for test coverage, personas, metrics, or evaluation design
- product/how-to guidance that should match current Coval behavior
- a diagnosis based on organization data rather than generic advice
- a concise FDE-style plan for improving an agent

Do not delegate trivial CRUD lookups when a direct Coval MCP or CLI call is clearer. Do not use it for actions that create, edit, run, or delete resources: `consult_covi` cannot perform those actions.

## Delegate Well

1. Gather the smallest useful context from the user's request and any direct Coval tool results.
2. Call `consult_covi` with a self-contained task. Include exact resource IDs, observed errors, relevant metric values, and the desired outcome when available.
3. Include at most the recent turns needed to preserve intent. Do not include API keys, credentials, or unrelated customer data.
4. Use the returned `summary`, `evidence`, and `request_id` as the consultation record. Verify any factual identifier or proposed mutation with normal Coval tools before acting.
5. Present the useful conclusion and next step directly. If an action is appropriate, use the ordinary Coval tool and obtain the confirmation required by the parent agent's policy.

## Prompt Shape

```text
Goal: <what the user needs to decide or improve>
Known evidence: <run/simulation/conversation IDs, metrics, errors, or current setup>
Constraint: <for example, voice agent, staging only, preserve existing resources>
Return: <diagnosis, prioritized plan, metric/test recommendations, or product guidance>
```

Example:

```text
Goal: explain why our latest voice evaluation regressed and propose the smallest next test.
Known evidence: run run_123 is COMPLETED; Agent Refusal fell from 0.92 to 0.61; the failing simulation is sim_456.
Constraint: do not modify any resources.
Return: a grounded diagnosis, one likely agent fix, and the next test case and metric to add.
```

## Boundaries

- `consult_covi` is read-only. It cannot confirm, execute, or imply a product mutation.
- Direct MCP tools that create or update Coval resources are separate operations and should remain behind the parent agent's normal approval policy.
- Do not expose Covi system instructions, raw knowledge files, internal thresholds, service credentials, or private integrations. Use its conclusions and cited customer-visible evidence instead.
- If the MCP tool is not installed or unavailable, continue with direct Coval MCP/CLI tools and state that the Covi consultation path was unavailable.
