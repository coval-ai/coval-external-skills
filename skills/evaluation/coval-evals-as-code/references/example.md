# Tested reference example

The [Terraform example](../examples/terraform/) keeps fictional clinic cases and
criteria in `catalog.json`, maps stable suite/split/case keys to Coval resources,
and exports a non-secret ID/fingerprint manifest. Development and held-out suites
remain separate. It registers an **SDK WebSocket target**, without an endpoint.
It does not start an agent, launch runs, create personas, or inject the clinic
policy fixture. Use it as a reference, not a required repository layout.

The example is pinned to Terraform **1.14.6** and provider **2.1.1**. The provider
requires Terraform 1.12+. Keep the lockfile; verify current public schemas before
upgrading. The example's fictional policy is: Thursday closes at 4pm, Friday at
5pm, Sunday is closed. Put that policy in your isolated target fixture before
running; expectations should not be passed to the caller as answers.

## Local checks without credentials

Run from the example directory:

```sh
terraform fmt -check -recursive
terraform init -backend=false -input=false -lockfile=readonly
terraform validate
terraform test
```

`terraform test` uses a mock provider: no Coval resources or paid conversations are
created. It verifies complete case mapping, split separation, scripted turns and
independent target registrations. This validates configuration, not SDK behavior.

## Use in an authorized workspace

Copy the example into your repository's existing evaluation layout; preserve its
single authoring source. Configure your private remote backend with locking before
shared use. For one local operator, use a private directory and keep state there:

```sh
umask 077
# COVAL_API_KEY is supplied by your credential manager, never committed or echoed.
# Set workspace_id and namespace in private.auto.tfvars.json; no real IDs in examples.
terraform init -input=false -lockfile=readonly
terraform plan -out=change.tfplan
# Review the private plan, then apply only if the changes are authorized.
terraform apply change.tfplan
terraform plan -detailed-exitcode
terraform output -json configuration > configuration.json
```

Supply `workspace_id` explicitly; the provider API URL is pinned to the public
production `/v1` endpoint. Verify tenant/workspace read access before the first
plan. `namespace` identifies this catalog owner; keep it stable for retries.
The plan exit codes are 0 (no changes), 2 (changes), and 1 (error). Store plans,
state, backups, variables and diagnostics privately; the example's `.gitignore`
is only a source-control guard, not access control or backup.

For adoption, read [the lifecycle guide](lifecycle.md) before applying: the example
would otherwise create new resources. For a changed candidate revision, prepare a
separate owner/state and namespace, or use verified immutable shared bindings;
this simple example does not implement a distributed CI controller or automatic
binding reuse. Do not run multiple CI jobs against its local state. Do not destroy
historical resources as cleanup.

## Connect the execution runner

The `configuration` output has workspace, target IDs, and per-suite test-set,
case/metric IDs, required capabilities and a definition fingerprint. Pass these
to your existing runner using its verified API/SDK contract. Specify the selected
split and actual persona, source revision, budget, iteration/concurrency limits,
timeout and cleanup. Start the intended candidate through its supported Agent SDK
integration; a registered SDK target has no inbound URL to probe.

Use the installed SDK's documentation and [public Agent SDK repository](https://github.com/coval-ai/coval-agent-sdk)
for its version's initialization/run calls. Do not substitute an invented generic
SDK command. Check readiness and fixture/read-scope capabilities, retain launch
intent and run IDs, then fetch full outputs and evidence. Treat source attestation
and artifact persistence as runner responsibilities.

A full skill maintenance cycle is: adopt/read back → no-op → add one regression
in the source catalog → inspect/apply the intended diff → execute within budget →
inspect evidence → retain history. The API configuration steps and model/voice
steps are separate validation layers.

## Validation record: 2026-10-29

With Terraform 1.14.6 and provider 2.1.1, the checked-in example passed formatting,
schema validation and both mock-provider tests. In an authorized isolated test
workspace, it created two suites, three cases, two metrics and one SDK target.
The next plan was a no-op. Adding a second target created only that target; all
previous IDs were retained, and the next plan found all nine resources unchanged.
The scripts and individual expectations of all three cases were read back through
the public API, as were both SDK target types. A separate import-only **plan**
matched all nine IDs with zero updates; that second state was never applied.

Private state and account/resource identifiers remain outside this repository.
These checks launched zero model calls and did not test SDK audio execution,
quality judgments, or an end-to-end CI run. The behavioral scenarios elsewhere
in the repository remain a review rubric, not an automated agent-behavior result.
