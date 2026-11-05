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
target cleanup; unrelated process arguments can expose credentials. Read every result page and verify scope. A shared seed
can select cases; it does not make conversations deterministic.

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
