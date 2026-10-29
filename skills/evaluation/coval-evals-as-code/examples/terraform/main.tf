terraform {
  required_version = ">= 1.12.0, < 2.0.0"
  required_providers {
    coval = {
      source  = "coval-ai/coval"
      version = "2.1.1"
    }
  }
}

provider "coval" {
  api_base_url = "https://api.coval.dev/v1"
  # Authentication is provided through COVAL_API_KEY.
}

variable "workspace_id" {
  type        = string
  description = "Explicit workspace verified against the intended account."
  validation {
    condition     = length(trimspace(var.workspace_id)) > 0
    error_message = "An explicit workspace is required."
  }
}

variable "namespace" {
  type        = string
  description = "Stable owner/revision name; a different name alone does not isolate state."
  default     = "clinic-reference"
}

variable "targets" {
  type        = set(string)
  description = "Independently owned SDK target names. No runtime or paid run is started."
  default     = ["candidate"]
}

locals {
  catalog = jsondecode(file("${path.module}/catalog.json"))
  cases = merge([for suite_key, suite in local.catalog.suites : {
    for case in suite.cases : "${suite_key}/${case.case_id}" => merge(case, { suite_key = suite_key })
  }]...)
}

resource "coval_test_set" "suite" {
  for_each      = local.catalog.suites
  display_name  = "${var.namespace}/${each.key}"
  test_set_type = "SCENARIO"
  tags          = ["evals-as-code"]
  workspace_id  = var.workspace_id
  lifecycle { prevent_destroy = true }
}

resource "coval_test_case" "case" {
  for_each           = local.cases
  test_set_id        = coval_test_set.suite[each.value.suite_key].id
  input_type         = "SCRIPT"
  input_str          = each.value.script_turns[0]
  script_turns       = jsondecode(jsonencode(each.value.script_turns))
  expected_behaviors = each.value.expected_behaviors
  description        = each.value.source
  workspace_id       = var.workspace_id
  lifecycle { prevent_destroy = true }
}

resource "coval_metric" "criteria" {
  for_each         = local.catalog.suites
  metric_name      = "${var.namespace}/${each.key}/criteria"
  description      = local.catalog.metric.description
  metric_type      = local.catalog.metric.metric_type
  criteria_source  = local.catalog.metric.criteria_source
  criteria_path    = local.catalog.metric.criteria_path
  reporting_method = local.catalog.metric.reporting_method
  workspace_id     = var.workspace_id
  lifecycle { prevent_destroy = true }
}

resource "coval_agent" "target" {
  for_each     = var.targets
  display_name = "${var.namespace}/${each.key}"
  model_type   = "MODEL_TYPE_SDK_WEBSOCKET"
  metadata     = {}
  tags         = ["evals-as-code"]
  workspace_id = var.workspace_id
  lifecycle { prevent_destroy = true }
}

# Only configuration IDs and definition fingerprints; no metadata or credentials.
output "configuration" {
  value = {
    workspace_id = var.workspace_id
    target_ids   = { for key, target in coval_agent.target : key => target.id }
    suites = {
      for key, suite in local.catalog.suites : key => {
        test_set_id           = coval_test_set.suite[key].id
        test_case_ids         = { for case in suite.cases : case.case_id => coval_test_case.case["${key}/${case.case_id}"].id }
        metric_ids            = [coval_metric.criteria[key].id]
        required_capabilities = suite.required_capabilities
        definition_sha256     = sha256(jsonencode({ suite_key = key, suite = suite, metric = local.catalog.metric }))
      }
    }
  }
}
