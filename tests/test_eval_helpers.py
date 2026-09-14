"""Synthetic behavioral checks, not customer validation or human-label evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = load('planner', 'skills/runs/quick-eval/scripts/plan.py')
fetcher = load('fetcher', 'skills/runs/quick-eval/scripts/fetch_run.py')
calibration = load('calibration', 'skills/evaluation/coval-calibrate-metric/scripts/calibration.py')


def launch(cases=1, mutations=0):
    body = {'agent_id': 'agent', 'persona_id': 'persona', 'test_set_id': 'set', 'metric_ids': ['metric'],
            'options': {'test_case_ids': [f'case-{i}' for i in range(cases)], 'iteration_count': 1, 'concurrency': 1},
            'config_overrides': {'simulation_timeout_seconds': 120}}
    if mutations:
        body['mutation_ids'] = [f'mutation-{i}' for i in range(mutations)]
    return body


def row(i, human=1, judge=1, **overrides):
    result = {'conversation_id': f'conversation-{i}', 'group_id': f'group-{i}', 'annotation_id': f'annotation-{i}',
              'reviewer': 'synthetic-fixture-provenance-claim', 'label_source': 'human', 'review_status': 'COMPLETED',
              'human_label': human, 'judge_label': judge, 'metric_status': 'COMPLETED', 'metric_id': 'metric-fixture',
              'metric_version': 'version-fixture', 'split': 'dev'}
    return {**result, **overrides}


def dataset(rows):
    return {'metric_id': 'metric-fixture', 'metric_version': 'version-fixture', 'rubric_id': 'rubric-fixture', 'records': rows}


class PlanTests(unittest.TestCase):
    def test_one_call_counts_metrics_and_duration(self):
        result = planner.plan(launch(), 3, 1)
        self.assertEqual(result['simulations'], 1)
        self.assertEqual(result['requested_metric_evaluations'], 1)
        self.assertEqual(result['configured_total_call_minutes_upper_bound'], 2)

    def test_mutations_include_base_and_repeat_count(self):
        body = launch(3, 2)
        body['options']['iteration_count'] = 2
        self.assertEqual(planner.plan(body, 18, 1)['simulations'], 18)

    def test_single_mutation_includes_base(self):
        body = launch()
        body['mutation_id'] = 'mutation'
        self.assertEqual(planner.plan(body, 2, 1)['simulations'], 2)

    def test_matrix_over_budget_rejected(self):
        body = launch(39, 2)
        body['options']['iteration_count'] = 2
        with self.assertRaises(ValueError):
            planner.plan_batch([body, body], 6, 1)

    def test_personas_share_one_batch_budget(self):
        with self.assertRaises(ValueError):
            planner.plan_batch([launch(3), launch(3)], 3, 1)
        self.assertEqual(planner.plan_batch([launch(3), launch(3)], 6, 1)['simulations'], 6)

    def test_reject_full_suite_omission(self):
        body = launch()
        del body['options']['test_case_ids']
        with self.assertRaises(ValueError):
            planner.plan(body, 100, 1)

    def test_reject_duplicate_cases(self):
        body = launch()
        body['options']['test_case_ids'] *= 2
        with self.assertRaises(ValueError):
            planner.plan(body, 100, 1)

    def test_reject_missing_duration(self):
        body = launch()
        body['config_overrides'] = {}
        with self.assertRaises(ValueError):
            planner.plan(body, 3, 1)

    def test_reject_concurrency_escalation(self):
        body = launch()
        body['options']['concurrency'] = 2
        with self.assertRaises(ValueError):
            planner.plan(body, 3, 1)

    def test_reject_conflicting_mutations(self):
        body = launch(1, 1)
        body['mutation_id'] = 'other'
        with self.assertRaises(ValueError):
            planner.plan(body, 100, 1)

    def test_reject_random_and_explicit_subset(self):
        body = launch()
        body['options']['sub_sample_size'] = 1
        with self.assertRaises(ValueError):
            planner.plan(body, 3, 1)

    def test_reject_bool_negative_and_float_counts(self):
        for value in (True, -1, 1.5, 0):
            body = launch()
            body['options']['iteration_count'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                planner.plan(body, 3, 1)


class CalibrationTests(unittest.TestCase):
    def test_always_pass_hides_failures_in_agreement(self):
        rows = [row(i) for i in range(98)] + [row(i, 0, 1) for i in range(98, 100)]
        result = calibration.calculate(dataset(rows), 'dev')
        self.assertEqual(result['agreement']['rate'], 0.98)
        self.assertEqual(result['failure_detection_tnr']['rate'], 0)
        self.assertEqual(result['false_pass_rate']['rate'], 1)
        self.assertEqual(result['false_pass_rate']['denominator'], 2)

    def test_zero_is_a_valid_label(self):
        result = calibration.calculate(dataset([row(1, 0, 0)]), 'dev')
        self.assertEqual(result['confusion']['tn'], 1)
        self.assertIsNone(result['pass_recall_tpr']['rate'])
        self.assertEqual(result['evidence'], 'insufficient_evidence')

    def test_failed_and_null_scores_not_pass_or_zero(self):
        rows = [row(1, 1, None), row(2, 1, 1, metric_status='FAILED'), row(3, 0, 0)]
        result = calibration.calculate(dataset(rows), 'dev')
        self.assertEqual(result['scored'], 1)
        self.assertEqual(sum(result['excluded'].values()), 2)

    def test_pending_review_excluded(self):
        result = calibration.calculate(dataset([row(1, review_status='PENDING')]), 'dev')
        self.assertEqual(result['scored'], 0)

    def test_ai_labels_rejected(self):
        with self.assertRaises(ValueError):
            calibration.calculate(dataset([row(1, label_source='ai')]), 'dev')

    def test_group_leakage_rejected(self):
        rows = [row(1, group_id='same'), row(2, group_id='same', split='test')]
        with self.assertRaises(ValueError):
            calibration.calculate(dataset(rows), 'dev')

    def test_duplicate_reviewers_not_independent(self):
        a = row(1)
        b = {**a, 'reviewer': 'second-reviewer', 'annotation_id': 'second-annotation'}
        with self.assertRaises(ValueError):
            calibration.calculate(dataset([a, b]), 'dev')

    def test_versions_cannot_be_mixed(self):
        with self.assertRaises(ValueError):
            calibration.calculate(dataset([row(1, metric_version='other')]), 'dev')

    def test_arbitrary_number_not_thresholded(self):
        with self.assertRaises(ValueError):
            calibration.calculate(dataset([row(1, 1, 0.8)]), 'dev')

    def test_perfect_small_sample_has_uncertainty(self):
        result = calibration.interval(3, 3)
        self.assertLess(result['wilson_95'][0], 0.5)
        self.assertAlmostEqual(result['wilson_95'][1], 1)

    def test_repeated_groups_warn_about_independence(self):
        result = calibration.calculate(dataset([row(1, 0, 0, group_id='same'), row(2, group_id='same')]), 'dev')
        self.assertEqual(result['independent_groups'], 1)
        self.assertTrue(any('Repeated groups' in w for w in result['warnings']))

    def test_test_measurement_conditional_on_untouched_data(self):
        rows = [row(1, 0, 0, split='test'), row(2, split='test')]
        self.assertEqual(calibration.calculate(dataset(rows), 'test')['evidence'], 'held_out_measurement_if_untouched')


class EvidenceTests(unittest.TestCase):
    def test_pagination_keeps_filter_and_uses_page_token(self):
        calls = []

        def get(path, params):
            calls.append(copy.deepcopy(params))
            if 'page_token' not in params:
                return {'items': [{'id': 'a'}], 'next_page_token': 'next'}
            return {'items': [{'id': 'b'}]}

        result = fetcher.pages(get, '/fixture', 'items', {'filter': 'run_id="run"'}, 3)
        self.assertEqual(len(result), 2)
        self.assertEqual(calls[1]['filter'], calls[0]['filter'])
        self.assertEqual(calls[1]['page_token'], 'next')

    def test_repeated_page_token_rejected(self):
        with self.assertRaises(ValueError):
            fetcher.pages(lambda *_: {'items': [], 'next_page_token': 'same'}, '/fixture', 'items', {}, 10)

    def test_incomplete_read_rejected(self):
        with self.assertRaises(ValueError):
            fetcher.pages(lambda *_: {'items': [{'id': 1}], 'next_page_token': 'more'}, '/fixture', 'items', {}, 1)

    def test_error_shape_not_empty_dataset(self):
        with self.assertRaises(ValueError):
            fetcher.pages(lambda *_: {'error': 'denied'}, '/fixture', 'items', {}, 3)

    def fixture_get(self, foreign=False, duplicate=False):
        run_id, sim_id = 'R' * 22, 'S' * 22

        def get(path, params=None):
            if path == f'/runs/{run_id}':
                return {'run': {'run_id': run_id, 'status': 'COMPLETED', 'metadata': {'private': 'omit'}}}
            if path.endswith('/metrics'):
                return {'metrics': [{'metric_output_id': 'O' * 26, 'metric_id': 'M' * 22, 'status': 'FAILED', 'value': None}]}
            detail = {'simulation_id': sim_id, 'run_id': 'OTHER' if foreign else run_id, 'status': 'FAILED', 'has_audio': False,
                      'transcript': [], 'destination': {'private_endpoint': 'omit'}}
            if path == '/conversations/simulated':
                return {'simulated_conversations': [detail, detail] if duplicate else [detail]}
            return {'simulated_conversation': detail}

        return get

    def test_scoped_fetch_rejects_other_run(self):
        with self.assertRaises(ValueError):
            fetcher.snapshot(self.fixture_get(foreign=True), 'R' * 22, 'workspace', 3)

    def test_duplicate_simulation_rejected(self):
        with self.assertRaises(ValueError):
            fetcher.snapshot(self.fixture_get(duplicate=True), 'R' * 22, 'workspace', 3)

    def test_metric_history_keeps_distinct_outputs_and_completeness_flag(self):
        original = self.fixture_get()

        def get(path, params=None):
            if path.endswith('/metrics'):
                self.assertEqual(params['include_superseded'], 'true')
                return {'metrics': [
                    {'metric_output_id': 'old', 'metric_id': 'metric', 'value': 0,
                     'status': 'COMPLETED', 'subvalues_by_timestamp_truncated': True},
                    {'metric_output_id': 'new', 'metric_id': 'metric', 'value': 1, 'status': 'COMPLETED'}]}
            return original(path, params)

        result = fetcher.snapshot(get, 'R' * 22, 'workspace', 3)
        metrics = result['simulations'][0]['metrics']
        self.assertEqual([m['metric_output_id'] for m in metrics], ['old', 'new'])
        self.assertTrue(metrics[0]['subvalues_by_timestamp_truncated'])

    def test_failure_stays_failure_and_private_config_omitted(self):
        data = fetcher.snapshot(self.fixture_get(), 'R' * 22, 'workspace', 3)
        self.assertEqual(data['audit']['metric_statuses'], {'FAILED': 1})
        self.assertEqual(data['audit']['simulation_statuses'], {'FAILED': 1})
        self.assertNotIn('metadata', data['run'])
        self.assertNotIn('destination', data['simulations'][0])


if __name__ == '__main__':
    unittest.main()
