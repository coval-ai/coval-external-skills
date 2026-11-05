# Use the supported Coval surface

Discover the installed CLI rather than assuming a particular version:

```bash
coval --agent agent doctor
coval --agent agent manifest
coval --agent runs context
coval --agent reports context
```

Doctor verifies connectivity/authentication, not the intended tenant/workspace.
Establish scope separately before resource reads/writes. Use the customer's
scoped profile/connector and keep credentials out of output and source control.

The public schema index is `https://api.coval.dev/v1/openapi`. Fetch relevant
named schemas with `Accept: application/json`, for example:

```bash
curl -fsS -H 'Accept: application/json' \
  https://api.coval.dev/v1/openapi/reports
```

Discover agents, personas, cases/sets, metrics, runs, simulated conversations,
traces and reports. CLI context/help establishes installed syntax; live schemas
establish API support. Do not extrapolate undocumented write endpoints.

Existing skills in this repository, when installed:

- `personas-from-artifacts` and `build-test-suite` for persona/case design.
- `configure-metrics` and `configure-trace-metrics` for available measurements.
- `coval-calibrate-metric` for actual human-label validation.
- `quick-eval` for bounded launches and result audits.
- `coval-evals-as-code` for Terraform/Git-owned resources.
- `coval-compare-runs` for matched outcomes and interpretation.

Reuse where applicable; missing skills do not justify fabricated tools. Native
chat needs a compatible chat target. Acoustic/turn-taking claims about a voice
agent need actual voice conversations and audio evidence.

Keep a private manifest with scope/budget, source/config digests, per-arm
effective models, case/persona/fixture/metric versions, split assignments,
launch payloads and IDs, run links, limits, schedule/retries, counts and evidence.
Exclude secrets, signed URLs, Terraform state and sensitive raw interactions
from public artifacts. Track only owned process IDs and start times during local
target cleanup; unrelated process arguments can expose credentials. Read every
result page and verify scope. A shared seed can select cases; it does not make
conversations deterministic.

## Additional scoring and output history

Before rescoring a large cohort, test the metric on a few saved outputs with
known expected behavior and verify its runtime prerequisites. A failed
conversation can contain valid trace expense yet be ineligible for a metric
that requires a completed simulation. Treat `SKIPPED` as terminal, retain its
reason, and leave the value unavailable. Do not replace it with zero or present
a receipt-derived value as a native metric result.

Discover the current `conversations/simulated:rerunMetrics` contract and pass only
the intended metric IDs. A metrics-only request can also refresh automatic
measurements. Snapshot existing output IDs, versions and full values before the
request; afterward verify the requested additions, unchanged primary scores and
any automatic refreshes. A changed latest-output pointer does not necessarily
mean historical evidence was deleted. Read the original output ULIDs and disclose
the side effects, including whether refreshed values and versions agree.

Test-metric executions can use an `INTERNAL` trigger that ordinary conversation
views hide. A not-found response on a conversation metric route is therefore not
proof that the test failed or its output vanished. The public
`metrics/outputs:batchGet` operation reads saved outputs by their returned ULIDs,
including test outputs; its HTTP POST is a read, not another scoring admission.
Verify scope, exact output/version IDs, terminal status and runtime metadata.
Save admission intent before non-idempotent scoring calls and reconcile uncertain
responses instead of submitting the whole batch again.

## Prepare native human review when needed

If automated judges fail qualification, preserve their outputs and prepare an
authorized Human Review project rather than manufacturing human labels. Select
a useful development panel, link its applicable metric criteria, leave labels
blank, and explain that the panel does not estimate population prevalence.
Use the requested reviewers and notification settings; creating a review queue
does not authorize contacting additional people.

Enable the actual native Blind Review setting when machine-score blindness is
required. An empty `blind_labeling_shown_metric_ids` list alone does not enable
it. Read back the setting or verify the deployed UI; model names can remain in
transcripts or traces, so distinguish machine-score blindness from model
blinding. Blind review and enforced disagreement notes can be incompatible;
preserve the intended priority and request evidence notes without claiming an
unsupported combination.

An API-created project can promote its sole reviewer to manager. Managers may
be excluded from aggregate progress by default even while their direct
assignments remain reviewable. Check assignments and saved labels separately
from aggregate counters. Use a supported progress-inclusion setting when
available; do not demote the last manager or add an unwanted reviewer to fix a
counter. Source code or a schema alone does not prove that a newer control is
deployed. Report the gap when the public API or live UI lacks it. Zero progress
is neither completed human labeling nor evidence that no work was assigned.

## Reports and notebooks

Inspect `reports create`, `get` and `rows` help/schema before saving. A report
is a view over run evidence, not proof of comparability. Identify arms and
grouping using supported fields. Default to private: the CLI warns that PUBLIC
reports also mark underlying runs public. Honor an authorized request to publish
a sanitized comparison after verifying that the exposed data is in scope.

Verify the grouping key on actual report rows. Metadata saved on a run may not
be propagated to its conversations; a saved metadata configuration can therefore
render no groups. When supported, use explicit custom dimensions whose simulation
memberships come from validated run attestations. Include failed simulations and
keep unassigned rows visible. Read the report revision/ETag and use `If-Match` for
view patches, then read back both memberships and the rendered grouped view.

Notebook authoring may not be exposed in public OpenAPI. Use an authorized editor
or first-party UI. Read-only assistant delegation does not authorize notebook
writes. Verify the document saved and opens in presentation mode. A local
outline is a fallback deliverable, not a platform notebook.

## Synthetic planning example

24 independent scenarios, one compatible persona assigned to each, three model
arms and three repeats produce `24 × 1 × 3 × 3 = 216` conversations. One smoke
per arm makes 219 before retries/additional scoring. Four applicable metrics
per main conversation produce up to 864 metric outputs, not 864 independent
observations or necessarily 864 billable judge calls. Include actual simulator
and metric implementation costs. Six reserved scenarios within the 24 are not
another six unless explicitly added. Stop at agreed bounds and reconcile
uncertain launches before retrying.

This is execution arithmetic, not evidence that an integration or agent passed.
