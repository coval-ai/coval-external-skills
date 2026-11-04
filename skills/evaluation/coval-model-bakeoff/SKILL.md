---
name: coval-model-bakeoff
description: Design and execute a controlled agent model or provider comparison in Coval, using traffic-grounded personas, matched regression cases, quality and efficiency metrics, and an evidence-backed recommendation.
---

# Compare the models behind an agent

Help the user decide whether a model swap improves their actual agent. Preserve
the agent's behavior and evaluation inputs so the model is the intended lever.
Use the customer's supported integration and Coval's public API or installed CLI.
No private infrastructure, internal harness or database access is required.

Read [study-design.md](references/study-design.md) for coverage, measurement and
decision design. Read [platform-workflow.md](references/platform-workflow.md) for
command discovery, resource ownership and reporting.

## Establish the decision before spending

Confirm the intended organization/workspace and whether the agent is chat,
voice or multimodal. Inspect effective configuration: primary model, provider,
reasoning settings, service tier, fallback chain, tools, prompts, memory, limits
and integration version. Source defaults alone do not establish the running model.

Propose a control plus useful alternatives. For a same-provider study, choose a
capability-oriented and an efficiency-oriented candidate using current official
provider documentation. Cite exact IDs and dated prices; verify account access
and compatibility. A smaller model is not necessarily worse on this agent.
Include another provider only when it serves the user's question.

Present exact candidates, settings, expected tradeoffs, execution count and cost
assumptions. Obtain any requested model confirmation before simulations. Resource
preparation does not authorize inference calls, runs, rescoring or paid previews.
Use the agreed execution budget, counting smokes, every arm, repeats, mutations,
simulator/judge usage and retries. If prices or token volumes are unknown,
propose a bounded pilot rather than inventing a dollar estimate. Turn, token,
time and concurrency limits are controls, not guaranteed provider spending caps.

## Freeze a reproducible study

Use one pinned agent revision for every arm, changing only the intended model
configuration. Explain necessary adapter differences. Hold prompts, tool
schemas, fixtures, permissions, retrieval, memory snapshots, personas, simulator,
judge, reasoning policy, timeouts and execution limits fixed. Record requested
and effective settings separately; do not silently drop unsupported settings.

For a pure model comparison, prevent cross-model fallback or analyze fallback
conversations separately. Otherwise the candidate can receive credit for another
model's answer. Evaluate production routing separately if that is also a question.

Reuse the customer's existing harness and resource owner. If configuration is
managed as code, edit and plan through that owner rather than creating a competing
API-managed catalog. Use isolated targets and approved fixtures. Keep temporary
endpoints alive until runs finish and credentials out of logs and Git. Do not
change the production model or customer resources to manufacture test coverage.

## Build coverage from behavior and capabilities

Reuse suitable cases, personas and metrics after checking their actual content.
Analyze an authorized recent interaction cohort: record exact dates, source,
pagination, inclusion rules and missing surfaces. Separate human activity from
automations and previous simulations. A partial cohort is a sample, not the
whole user population.

Derive behavioral personas from observed goals, domain fluency, request detail,
follow-up style and constraints. Preserve counts and provenance privately. Avoid
inferred demographics and identifiable conversation copies. Convert real asks
into synthetic scenarios with independently checkable expectations; historical
assistant answers are not ground truth.

Combine a representative traffic slice with a capability matrix and a separate
risk/regression slice. Cover normal requests, ambiguity, corrections, long
histories, tool errors, empty data, pagination, scope/permission boundaries, and
proposal-versus-completed-action truthfulness where applicable. Include multi-turn
journeys. Run compatible persona/case combinations rather than multiplying
every persona by every case blindly.

Scripted user turns may bypass persona generation. Verify simulator behavior:
fixed scripts support paired regressions, while adaptive scenarios exercise
personas. Creating a persona resource alone does not establish persona coverage.

For each case record stable key, source category, persona, fixture/version,
required capabilities, expected tools, forbidden side effects, outcome and split.
Missing fixtures are explicit gaps. Keep held-out cases for a checkpoint, without
tuning prompts or judges to their scores.

## Measure outcomes and the work required

Declare primary success and regression rules before looking at results. Add
diagnostics for quality, latency, cost and tool behavior without hiding mandatory
failures inside a weighted mean.

Prefer existing validated metrics. Inspect criterion, units, direction,
applicability, judge/version and missing-value behavior. Use trace or fixture
assertions for exact arguments, scope, side effects and factual counts. Use judges
for qualitative behavior, with frozen rubrics and evidence-backed disagreement
review. Transcript-only judges cannot establish executed tools or successful writes.

Configure additional criteria for actual gaps. Preview against authorized known
successes and failures within budget. Human calibration requires human labels;
an agent's adjudication is not human validation. Missing traces, usage fields or
timestamps remain unavailable rather than zero, pass, or inferred precision.

Choose metrics appropriate to the modality. Audio silence-gap latency does not
measure chat responsiveness. Model-call duration is not time to first token.
Verify trace correlation and actual timing emission before claiming either.

## Execute and audit

After approval, smoke-test each arm. Check effective model, matched inputs,
isolation, trace correlation, token accounting and metric completion before
expanding. Stop to diagnose invalid primary measurements. Missing optional
diagnostics can remain disclosed gaps while valid quality evaluation continues.
Keep smokes separate when configuration changes afterward.

Interleave/randomize arms in comparable blocks and retain the schedule. Shared
rate limits, fixture drift, cold starts and upstream incidents can dominate
latency. Use equal concurrency and record conditions. Reconcile uncertain launch
responses before retrying; retain intent/request IDs to avoid duplicate spending.

Audit requested, admitted, observed, terminal, validly scored, failed, skipped,
unavailable and matched counts. Match immutable case content/persona/condition,
not list position. Repeats estimate within-case variation, not new coverage.
Review every critical failure and changed outcome plus a blinded sample of
unchanged outcomes.

## Deliver an inspectable recommendation

Create a Coval comparison report from approved run IDs, private by default.
For requested public sharing, prepare a sanitized run set, explain that public
settings can also expose underlying runs, and verify publication authority covers
that data. Honor explicit public-sharing instructions; ask only for missing
authority. Keep the decision run set stable, identify each arm, and include
case-level regressions and missingness.

Use the supported notebook editor, if available, to present the question,
configuration, coverage, quality, latency, cost, tool behavior, failures,
uncertainty and recommendation. Link claims to saved run/metric evidence. If
notebook authoring is unavailable, provide the report and presentation-ready
outline; do not invent an API or call an unsaved outline a completed notebook.

Report a measured recommendation, conditional recommendation or inconclusive
result. Distinguish development performance, held-out evidence and production
acceptance. Name untested delivery, UI, memory, scheduling and confirmed-write
surfaces. A model recommendation does not authorize rollout.

Keep a private work log of hypotheses, immutable inputs, actual commands,
friction, corrections and evidence. Public documentation should retain reusable
mechanics and synthetic examples, excluding raw transcripts, identities,
tenant/resource IDs, credentials, private routes/infrastructure and unpublished
customer results. Mark unexecuted steps as planned.
