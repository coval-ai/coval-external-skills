---
name: create-dashboard
description: Create a new Coval dashboard and populate it with metric widgets. Use when user says "create a dashboard", "build a dashboard", "visualize my metrics", "set up a performance dashboard", or "make a dashboard for my runs".
argument-hint: "[dashboard-name]"
---

# Create Coval Dashboard

Create a new dashboard for `$ARGUMENTS`.

## Instructions

### Step 1: Verify CLI Authentication

```bash
coval whoami
```

If not authenticated, run `coval login` first.

### Step 2: Create the Dashboard

```bash
coval dashboards create --name "Dashboard Name"
```

Capture the dashboard ID from the output.

### Step 3: Identify Metrics

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

### Step 4: Add Widgets

For each metric, create a widget. Choose the visualization type based on the metric output:

| Metric Output | Recommended Visualization |
|---------------|--------------------------|
| Float (numeric) | `statistic`, `line`, `bar`, `histogram` |
| String (Yes/No) | `pie`, `bar` |
| String (categories) | `pie`, `bar`, `top-list` |

Before choosing widget sizes, consult `references/grid-layout.md` for the 48-column grid constraints and widget-type minimums.

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Widget Name" \
  --type chart \
  --width <columns> --height <rows> \
  --config '{"metricId": "<metric_id>", "visualizationType": "line", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

### Step 5: Verify Layout

After adding all widgets, list them and check the **returned** grid positions for gaps:

```bash
coval dashboards widgets list <dashboard_id> --format json
```

CRITICAL: Verify from the returned values:
- Each row's widgets sum to 48 columns wide
- No vertical gaps between rows
- Widget sizes respect type minimums per `references/grid-layout.md`

Fix any gaps by updating widget dimensions with `coval dashboards widgets update`.

## Example

```bash
# Create dashboard
coval dashboards create --name "Q1 Agent Performance"

# Add a latency statistic (16 cols wide, 12 rows tall)
coval dashboards widgets create <dashboard_id> \
  --name "Avg Latency" \
  --type chart \
  --width 16 --height 12 \
  --config '{"metricId": "29BlkepvvX19ebbLDB0y6Q", "visualizationType": "statistic", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float", "precision": 2, "units": "s"}'

# Verify layout
coval dashboards widgets list <dashboard_id> --format json
```

## Troubleshooting

### Widget created but not visible
Cause: Grid position (`grid_x`, `grid_y`) may be null after creation.
Solution: Update the widget with explicit grid positions using `coval dashboards widgets update`.

### Widget dimensions changed from what was requested
Cause: The server enforces minimum sizes per widget type.
Solution: Check `references/grid-layout.md` for constraints and use valid dimensions.

### "Invalid request body" error on widget create
Cause: Config JSON is malformed or missing required fields.
Solution: Chart widgets require all of: `metricId`, `visualizationType`, `monitoring`, `aggregation`, `metricOutputType`.
