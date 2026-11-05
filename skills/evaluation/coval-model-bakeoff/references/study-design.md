# Study design and measurement

## Coverage

Keep representative traffic coverage separate from capability/risk coverage.
The former reflects observed prevalence; the latter includes rare important
workflows. Failure-weighted suite scores do not estimate average production success.

| Behavior | Example persona | Expected evidence |
|---|---|---|
| Find a resource with vague terminology | First-time evaluator | Clarifies or retrieves the right scoped object |
| Diagnose a failure | Technical investigator | Reads evidence, distinguishes fact from hypothesis |
| Compare cohorts/windows | Operational analyst | Correct filters, denominators, units and boundaries |
| Configure an evaluation | Experienced builder | Valid proposal, preserves constraints |
| Recover after a failed tool | Impatient follow-up user | Bounded recovery, truthful next action |
| Continue a long workflow | Returning collaborator | Relevant history and corrections retained |

These are examples, not empirically established personas. Derive the actual
mixture from usage and capability ownership. Split by source thread/user or
scenario family to prevent near-duplicate leakage. Independently verify expected
outcomes, especially when the source is a known bad interaction.

## Metric menu

Select applicable metrics with available inputs. Separate mandatory outcomes
from diagnostics; more metrics do not automatically provide more evidence.

| Dimension | Measurements | Interpretation |
|---|---|---|
| Outcome | Task/journey success; mandatory failures; clarification | Exact denominators and case transitions |
| Grounding | Supported claims; retrieval relevance; numerical correctness | Hard facts need controlled data or receipts |
| Scope/permissions | Correct workspace/filter; confirmation; side effects | Critical failures stay visible beside means |
| Tools | Selection/arguments/order; errors; retries; redundant calls | Fewer calls help only when the task succeeds |
| Continuity | Correction uptake; references; history; recovery | Evaluate complete journeys |
| Reliability | Timeouts; empty responses; provider failures; fallback | Failed execution means missing quality evidence too |
| Responsiveness | First token; first useful answer; turn/task latency | Streaming, tool waits and total time are distinct |
| Distribution | Median/tail latency; paired deltas; warm/cold | Small samples cannot support strong tail claims |
| Efficiency | Calls; input/cached/output/reasoning tokens; tool time | Include failures, avoid nested-span double count |
| Money | Inference cost/task; cost/success; total study spend | Separate agent, simulator, judge and platform cost |

Use dated effective-provider tariffs and actual billable token categories.
For per-million pricing: `sum(tokens_by_category * price_by_category / 1_000_000)`.
Cached input may be a subset of input; reasoning tokens may already be included
in output. Follow the provider's schema to avoid charging overlapping categories
twice. Record service tier/cache assumptions. Token-derived cost is an estimate,
distinct from provider-reported or invoiced cost. Missing pricing is not zero.

Cost per successful task includes failed-attempt costs in the numerator and
independently judged successes in the denominator. With zero successes, show
undefined/infinite and the counts. Routing/retries remain operational costs even
when excluded from the pure-model contrast.

Report observed and missing cost counts per arm. Do not divide partial observed
cost by every success and call it whole-study cost per success. A measured-subset
ratio needs the matching subset's outcomes and a selection-bias caveat. Suppress
whole-study cost rankings until coverage is comparable, or provide justified
bounds accounting for missing calls and prices.

## Checks learned from live integrations

Inspect the provider's complete numerical usage categories. Cache-write tokens
may be separate from cached reads and ordinary input; legacy retention settings
may differ from billing write TTL. Partition overlapping categories using current
official billing rules. Preserve whether TTL came from provider metadata, an
explicit request, or a verified default. A missing native price entry does not
mean a new model is free.

Count actual target requests as well as visible dialogue. A simulator can request
an opening greeting in addition to the scripted user turns. Include its spend in
the study total and label startup overhead. Do not subtract that call to claim a
production counterfactual: it may prime later cache and conversation history.

Inspect saved per-criterion outcomes and their unknown counts, not only a metric's
number or configured presentation. Preserve a raw fractional score separately
from any derived all-mandatory-criteria pass rule. A transcript-only judge can call
real but unfamiliar resource names invented; verify actual tool receipts and
independent scoped facts before classifying that as an agent regression. A
trace-aware judge remains provisional until its own errors are measured.

Verify actual stored trace fields and complete span counts. Export acceptance is
not read-back proof; fixtures must mirror the supported wire schema. Check the
installed configuration provider as well as live API schemas: an older provider
may support a custom trace equivalent while lacking a newer built-in metric type.

Qualify each expensive evaluator on saved pilot outputs before attaching it to
hundreds of conversations. A terminal metric can still return UNKNOWN because its
own context or tool budget is exhausted. Preserve that output as an evaluation
failure; it is not an agent failure. Exclude unqualified diagnostics from the
broad batch, or version a bounded replacement and validate it separately. Runtime
trace-context metadata and a failed trace selector are not proof that stored
traces are absent; inspect the actual scoped read-back. Tool argument spans alone
do not establish the exact payload returned by the tool.

## Analysis and presentation

Match case content and compatible persona conditions. Keep requested, terminal,
scored and matched counts distinct; nulls are unavailable. Report binary
pass/fail transitions and unit-aware numerical per-case deltas/distributions.
Use case/source-group uncertainty estimates when supported; turns and repeats
are not independent cases. Predeclare primary metrics/tolerances. Exploratory
slices across many metrics suggest follow-ups rather than proving superiority.

Show a Pareto view of quality, latency and cost. A cheap model that handles simple
traffic but fails complex workflows may justify a conditional recommendation.
It does not prove a proposed router will work; routing needs its own evaluation.

Suggested slides:

1. Decision/recommendation, or why it remains inconclusive.
2. Control/candidates and effective settings/source/fixture versions.
3. User behaviors, cohort completeness and sampling limitations.
4. Capability coverage and untested surfaces.
5. Task success and critical regressions.
6. Latency and tool waits.
7. Usage, dated cost estimates and cost per success.
8. Trace-backed wins/failures and judge disagreements.
9. Uncertainty and production qualification gaps.
10. Smallest next decision or confirmation experiment.

Every chart needs units, denominator, source runs and missingness. Avoid an
overall score that conceals a mandatory failure.
