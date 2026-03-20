---
name: add-widget
description: Add a chart, table, or text widget to a Coval dashboard. Use when user says "add a widget", "add a chart", "add a metric to the dashboard", "put a graph on my dashboard", or "add visualization".
argument-hint: "[dashboard-id]"
---

# Add Widget to Dashboard

Add a widget to dashboard `$ARGUMENTS`.

## Instructions

### Step 1: Verify CLI Authentication

```bash
coval whoami
```

If no dashboard ID provided, list available dashboards:

```bash
coval dashboards list
```

### Step 2: Determine Widget Type

Ask the user what they want to add:

| Type | Description | Use For |
|------|-------------|---------|
| `chart` | Metric visualization | Line charts, bar charts, pie charts, statistics, histograms |
| `table` | Metric comparison table | Side-by-side metric values |
| `text` | Markdown text block | Notes, descriptions, headers |

### Step 3: Configure Widget

#### For Chart Widgets

Identify the metric:

```bash
coval metrics list
coval metrics list --include-builtin
```

Build the config JSON. Required fields: `metricId`, `visualizationType`, `monitoring`, `aggregation`, `metricOutputType`.

See `references/grid-layout.md` for the full config reference and valid values.

#### For Table Widgets

```json
{"metricIds": ["id1", "id2"], "monitoring": "Simulations", "aggregation": "avg"}
```

#### For Text Widgets

```json
{"text": "## Section Header\nMarkdown content here."}
```

### Step 4: Choose Size

Consult `references/grid-layout.md` for the 48-column grid constraints and widget-type minimums before choosing dimensions.

### Step 5: Create Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Widget Name" \
  --type <chart|table|text> \
  --width <columns> \
  --height <rows> \
  --config '<json>'
```

### Step 6: Verify

CRITICAL: Check the **returned** grid values — the server may adjust dimensions to enforce minimums:

```bash
coval dashboards widgets list <dashboard_id> --format json
```

Ensure no gaps in the layout (all rows sum to 48 columns, no vertical gaps).

## Examples

### Statistic Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Avg Latency" \
  --type chart \
  --width 16 --height 12 \
  --config '{"metricId": "29BlkepvvX19ebbLDB0y6Q", "visualizationType": "statistic", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float", "precision": 2, "units": "s"}'
```

### Line Chart Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Latency Over Time" \
  --type chart \
  --width 24 --height 8 \
  --config '{"metricId": "29BlkepvvX19ebbLDB0y6Q", "visualizationType": "line", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

### Table Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Metrics Overview" \
  --type table \
  --width 48 --height 8 \
  --config '{"metricIds": ["29BlkepvvX19ebbLDB0y6Q", "7VHk6dTjvBcuV6XYPmaeGq"], "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

## Troubleshooting

### "Invalid request body" error
Cause: Config JSON is malformed or missing required fields.
Solution: Chart widgets require all of: `metricId`, `visualizationType`, `monitoring`, `aggregation`, `metricOutputType`.

### Widget created with null grid positions
Cause: The API does not auto-assign `grid_x`/`grid_y` on creation.
Solution: Update the widget with explicit positions using `coval dashboards widgets update`.

### Widget dimensions differ from requested
Cause: The server enforces minimum sizes per widget type.
Solution: Consult `references/grid-layout.md` for valid dimensions.
