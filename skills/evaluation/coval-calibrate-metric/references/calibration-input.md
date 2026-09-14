# Binary calibration input

Create this local JSON from actual completed human annotations and the exact
candidate metric outputs. Retain the raw source export privately for audit.
The following is a **schema illustration**, not human-labeled evidence:

```json
{
  "metric_id": "metric-example",
  "metric_version": "version-example",
  "rubric_id": "Friday-hours-v1",
  "records": [
    {
      "conversation_id": "conversation-example",
      "group_id": "original-case-example",
      "split": "dev",
      "annotation_id": "annotation-example",
      "reviewer": "actual reviewer identifier",
      "label_source": "human",
      "review_status": "COMPLETED",
      "human_label": 0,
      "judge_label": 1,
      "metric_status": "COMPLETED",
      "metric_id": "metric-example",
      "metric_version": "version-example"
    }
  ]
}
```

Labels are numeric 0/1 or strings `PASS`/`FAIL` (case-insensitive). No implicit
thresholds for arbitrary numbers, truthiness conversion or missing-as-fail.
`human_label` comes from `ground_truth_float_value` or `ground_truth_string_value`;
`judge_label` comes from the exact metric output's `value`, normalized according
to the rubric. Coval binary judges can return `YES`/`NO` or `Yes`/`No`; explicitly
map them to 1/0 only after establishing which answer means the desired behavior.
A judge asking whether a failure occurred reverses that mapping. Preserve the
raw value and mapping in the source audit; never use string truthiness. `metric_version` is
the output's `metric_version_ulid`, verified against the frozen candidate.

Include rows for train/dev/test to detect cross-split leakage. Put all near-
duplicates, repeat runs and variants of one source case into one group. The
calculator reports per-call results and explicitly warns when several calls
share a group: its simple binomial intervals assume independence and cannot
establish independent confidence for correlated repetitions.

Choose one adjudicated human label per conversation. Keep a link to the original
annotations and the expert's adjudication in the private source record; don't
double-count reviewer rows. The calculator rejects duplicate conversation IDs.

Pending/deferred annotations and non-completed metric outputs are counted as
excluded by reason. AI labels are rejected, not silently discarded. Unknown
version identity or mixed candidate versions prevents a version-specific result.
No network calls, re-scoring, label changes or automatic release decisions occur.
