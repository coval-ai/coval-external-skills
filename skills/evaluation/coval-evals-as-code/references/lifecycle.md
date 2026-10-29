# Configuration lifecycle

## Adoption and a normal regression change

1. Inventory the selected workspace with paginated public API/CLI reads. Compare
   exact IDs, scripts, criteria and metadata with the repository. If multiple historic
   resources match, choose one canonical binding explicitly and retain the others.
2. Record state ownership and bindings. Only one state may manage an object; a
   consumer can reference its ID or use a data source without importing it again.
3. Write configuration matching the current objects, then add import blocks with
   the actual ID and explicit workspace. Terraform 1.12+ supports provider resource
   identities. This example targets the supplied sample's test-set address:

   ```hcl
   import {
     to = coval_test_set.suite["clinic/development"]
     identity = {
       id           = "REPLACE_WITH_EXISTING_TEST_SET_ID"
       workspace_id = var.workspace_id
     }
   }
   ```

   Import cases, metrics and target registrations too when adopting them. Verify
   each address against the configuration. The import plan must preserve content;
   inspect optional fields and metadata rather than overwriting an existing target
   with the minimal starter example. Do not import the same remote object into two
   candidate states. See the pinned [resource docs](https://github.com/coval-ai/terraform-provider-coval/tree/v2.1.1/docs/resources).
4. Inspect the full private plan, apply only the agreed changes, read back exact
   contents/IDs and verify a subsequent no-op. Imports retain IDs/history; an apply
   that also updates definitions is not a pure adoption.
5. Add the regression to the authoritative source, keep expectations separate from
   caller input, and reuse appropriate personas/metrics. Review the next plan and
   inspect evidence after an authorized run. For shared mutable suites, serialize
   edits and exclude active consumers before changing the definitions.

An import timeout or lost apply response can leave resources created remotely.
Inspect retained state and scoped remote inventory before retrying. Back up/recover
state through the configured backend. Never delete state to make a plan green.

## Concurrent candidates and history

A source SHA alone does not prove which hosted cases were used. Record a fingerprint
covering the selected cases, expected behaviors, metric configuration, split and
required fixtures. Record persona/fixture versions and the target source separately.
A matching content hash across different suite/split identities is insufficient.

Choose one explicit strategy:

- **Shared immutable definitions:** canonical state owns published fixtures; each
  attempt reads exact bindings and owns its target. Changed definitions get a new
  version with an independent state/namespace. Retain old bindings and history.
- **Candidate workspace:** each independently scoped state owns definitions and
  targets in that workspace. Verify prerequisite personas, permissions and fixtures;
  workspace isolation does not populate them automatically.

Do not merely rename a resource in the same state and call it isolated. Likewise,
copying state into another writer makes both states manage the same remote IDs.
An existing attempt must retain its original binding choice across retries even if
canonical bindings appear, disappear or change later. Review state migrations
explicitly. `prevent_destroy` protects declared resources, not blocks removed from
configuration; inspecting deletes/replacements remains necessary.

Target bearer rotation or endpoint changes must affect only the intended target.
Keep unrelated metadata when importing/updating it. Stop target/tunnel processes on
success, failure and cancellation; retain resources and private state according to
the customer's history/retention policy. Do not add automatic destroy on CI exit.

## Provider and API details discovered in lifecycle testing

These are observed behaviors with provider **2.1.1**; recheck on upgrades rather
than treating a workaround as permanent policy.

- The API normalizes tags to lowercase. Author canonical lowercase tags and check
  import/no-op behavior; don't repeatedly apply capitalization-only drift.
- `script_turns` is a dynamic JSON value. A Terraform typed list can compare
  differently from the provider's JSON tuple despite identical displayed JSON.
  `jsondecode(jsonencode(turns))` supplies the expected dynamic representation.
  Inspect typed values before suppressing a difference.
- Omitted, null and empty fields can have different preservation/clearing semantics.
  Read the resource schema before updating imported metadata or optional lists.
- `sensitive` redacts normal displays; state, plans and JSON diagnostics remain
  sensitive. An environment API key keeps it out of HCL but does not make all
  provider outputs safe to publish. Export selected fields only.
- Terraform manages configuration. It does not inject synthetic fixtures, implement
  SDK audio transport, host a target, verify permissions or decide quality gates.

## Acceptance cases

Exercise the relevant cases when changing lifecycle behavior. Use a separately
authorized disposable workspace for writes; the example's mock tests never call
the Coval API. A planning request authorizes neither writes nor paid runs.

| Exercise | Evidence required |
| --- | --- |
| Adopt an existing suite and target | Exact IDs/content retained; imports and zero unintended changes; history still accessible |
| Reapply without edits | No planned changes and identical resource IDs |
| Add/change a case | Only intended diff; correct script/individual expectations read back; older run evidence remains interpretable |
| Change candidate cases while another run is active | Distinct owned definition IDs or explicit immutable bindings; first run's content unchanged |
| Start two candidate targets | Different target IDs; rotating one target leaves the other untouched |
| Retry after ambiguous create/apply/launch | Reconciles retained state/intent; no duplicate object/run or changed bindings |
| Publish/remove a canonical binding during an attempt | Retry retains the attempt's original IDs and ownership |
| Missing fixture or API read scope | Preflight prevents launch where detectable; actual runtime denials retain evidence and an incomplete verdict |
| Judge says NOT_MET while its explanation describes success | Preserve score and explanation; inspect criterion/transcript and calibrate before gating |
| SDK agent registers successfully | Claim registration only until the candidate's audio execution and evidence are independently verified |

Record exact source/provider/Terraform versions and which tests used mocks, live
configuration or model calls. Keep real tenant IDs, keys, private run links and
customer conversations out of public examples and PR descriptions.
