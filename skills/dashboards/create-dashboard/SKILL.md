---
name: create-dashboard
description: Create a new Coval dashboard and populate it with metric widgets. Use when user wants to build a dashboard or visualize evaluation results.
argument-hint: "[dashboard-name]"
---

# Create Coval Dashboard

Create a new dashboard for `$ARGUMENTS`.

## Prerequisites

Ensure the Coval CLI is installed and authenticated:
```bash
coval whoami
```

If not authenticated, run `coval login` first.

## Workflow

### Step 1: Create Dashboard

```bash
coval dashboards create --name "Dashboard Name"
```

Capture the dashboard ID from the output.

### Step 2: Identify Metrics

List available metrics to populate the dashboard:

```bash
coval metrics list
coval metrics list --include-builtin
```

Ask user which metrics they want to visualize. If they want metrics from previous runs:

```bash
coval runs list --page-size 10
coval runs get <run_id> --format json
```

### Step 3: Add Widgets

For each metric, create a widget. Choose the visualization type based on the metric:

| Metric Output | Recommended Visualization |
|---------------|--------------------------|
| Float (numeric) | `statistic`, `line`, `bar`, `histogram` |
| String (Yes/No) | `pie`, `bar` |
| String (categories) | `pie`, `bar`, `top-list` |

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Widget Name" \
  --type chart \
  --config '{"metricId": "<metric_id>", "visualizationType": "line", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

### Step 4: Verify Layout

After adding all widgets, list them and check the returned grid positions for gaps:

```bash
coval dashboards widgets list <dashboard_id> --format json
```

Verify:
- Each row's widgets sum to 48 columns wide
- No vertical gaps between rows
- Widget sizes respect type minimums (see Grid Layout below)

Fix any gaps by updating widget dimensions.

## Grid Layout

The dashboard uses a **48-column** grid. Widget sizes must respect these constraints:

| Widget Type | Min Width | Min Height | Default Width | Default Height | Notes |
|-------------|-----------|------------|---------------|----------------|-------|
| `chart` | 12 | 8 | 12 | 8 | — |
| `chart` (statistic) | 10 | 12 | 12 | 12 | Max width: 24 |
| `table` | 4 | 8 | 48 (full width) | 8 | — |
| `text` | 12 | 2 | 16 | 2 | Fixed height of 2 |

**Important:** Always check the **returned** grid values from the API/CLI — the server may adjust your requested dimensions to enforce minimums.

## Widget Config Reference

### Chart Config

Required fields: `metricId`, `visualizationType`, `monitoring`, `aggregation`, `metricOutputType`

| Field | Values |
|-------|--------|
| `visualizationType` | `line`, `bar`, `area`, `statistic`, `pie`, `histogram`, `top-list` |
| `monitoring` | `Monitoring` (live conversations) or `Simulations` (test runs) |
| `aggregation` | `sum`, `count`, `avg`, `max`, `min`, `success` |
| `metricOutputType` | `string` or `float` |

Optional: `bucketInterval`, `groupBy`, `precision`, `units`, `showAsPercentage`, `filters`

### Table Config

Required fields: `metricIds`, `monitoring`, `aggregation`

### Text Config

Required fields: `text` (markdown content, max 10,000 chars)

## Example

```bash
# Create dashboard
coval dashboards create --name "Q1 Agent Performance"

# Add a latency statistic
coval dashboards widgets create <dashboard_id> \
  --name "Avg Latency" \
  --type chart \
  --width 16 --height 12 \
  --config '{"metricId": "29BlkepvvX19ebbLDB0y6Q", "visualizationType": "statistic", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float", "precision": 2, "units": "s"}'

# Add a turn count line chart
coval dashboards widgets create <dashboard_id> \
  --name "Turn Count Over Time" \
  --type chart \
  --width 24 --height 8 \
  --config '{"metricId": "7VHk6dTjvBcuV6XYPmaeGq", "visualizationType": "line", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'

# Verify layout
coval dashboards widgets list <dashboard_id> --format json
```
