mock_provider "coval" {}

variables {
  workspace_id = "fixture-workspace"
  namespace    = "fixture-catalog"
  targets      = ["attempt-a", "attempt-b"]
}

run "complete_catalog" {
  command = apply

  assert {
    condition     = length(output.configuration.suites) == 2 && length(coval_test_case.case) == 3
    error_message = "Every source suite/split and case must be represented."
  }
  assert {
    condition     = output.configuration.suites["clinic/development"].test_set_id != output.configuration.suites["clinic/held_out"].test_set_id
    error_message = "Development and held-out cases must have independent test sets."
  }
  assert {
    condition     = coval_test_case.case["clinic/development/day_correction"].script_turns[1] == "Sorry, I meant Friday."
    error_message = "The ordered script must retain the correction turn."
  }
  assert {
    condition     = coval_metric.criteria["clinic/development"].criteria_path == "expected_behaviors" && length(coval_test_case.case["clinic/development/friday_hours"].expected_behaviors) == 1
    error_message = "Criteria must come from the source case's individual expected behaviors."
  }
  assert {
    condition     = output.configuration.target_ids["attempt-a"] != output.configuration.target_ids["attempt-b"]
    error_message = "Concurrent attempts need separate target registrations."
  }
  assert {
    condition     = alltrue([for target in coval_agent.target : target.model_type == "MODEL_TYPE_SDK_WEBSOCKET" && target.workspace_id == var.workspace_id])
    error_message = "Targets must use the SDK connection and explicit workspace."
  }
  assert {
    condition     = output.configuration.suites["clinic/development"].required_capabilities == ["clinic_policy_fixture"]
    error_message = "Required execution fixtures must remain visible to the runner."
  }
}

run "same_inputs_noop" {
  command = plan

  assert {
    condition     = output.configuration == run.complete_catalog.configuration
    error_message = "An unchanged plan must retain IDs and definition fingerprints."
  }
}
