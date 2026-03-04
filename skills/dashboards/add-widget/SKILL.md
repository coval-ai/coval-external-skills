---
name: add-widget
description: Add a chart, table, or text widget to a Coval dashboard. Use when user wants to add a visualization or metric to a dashboard.
argument-hint: "[dashboard-id]"
---

# Add Widget to Dashboard

Add a widget to dashboard `$ARGUMENTS`.

## Prerequisites

Ensure the Coval CLI is installed and authenticated:
```bash
coval whoami
```

If no dashboard ID provided, list available dashboards:

```bash
coval dashboards list
```

## Workflow

### Step 1: Determine Widget Type

Ask the user what they want to add:

| Type | Description | Use For |
|------|-------------|---------|
| `chart` | Metric visualization | Line charts, bar charts, pie charts, statistics, histograms |
| `table` | Metric comparison table | Side-by-side metric values |
| `text` | Markdown text block | Notes, descriptions, headers |

### Step 2: Configure Widget

#### For Chart Widgets

Identify the metric:

```bash
coval metrics list
coval metrics list --include-builtin
```

Build the config JSON with required fields:

| Field | Description | Values |
|-------|-------------|--------|
| `metricId` | Metric to visualize | Metric ID string |
| `visualizationType` | Chart type | `line`, `bar`, `area`, `statistic`, `pie`, `histogram`, `top-list` |
| `monitoring` | Data source | `Monitoring` or `Simulations` |
| `aggregation` | Aggregation method | `sum`, `count`, `avg`, `max`, `min`, `success` |
| `metricOutputType` | Metric value type | `string` or `float` |

Optional fields: `bucketInterval`, `groupBy`, `precision`, `units`, `showAsPercentage`, `xAxisLabel`, `yAxisLabel`, `filters`

#### For Table Widgets

```json
{"metricIds": ["id1", "id2"], "monitoring": "Simulations", "aggregation": "avg"}
```

#### For Text Widgets

```json
{"text": "## Section Header\nMarkdown content here."}
```

### Step 3: Choose Size

Refer to the grid constraints (48-column grid):

| Widget Type | Min Width | Min Height | Default Width | Default Height | Notes |
|-------------|-----------|------------|---------------|----------------|-------|
| `chart` | 12 | 8 | 12 | 8 | — |
| `chart` (statistic) | 10 | 12 | 12 | 12 | Max width: 24 |
| `table` | 4 | 8 | 48 | 8 | Defaults to full width |
| `text` | 12 | 2 | 16 | 2 | Fixed height of 2 |

### Step 4: Create Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Widget Name" \
  --type <chart|table|text> \
  --width <columns> \
  --height <rows> \
  --config '<json>'
```

### Step 5: Verify

Check the **returned** grid values — the server may adjust dimensions to enforce minimums:

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

### Pie Chart Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Agent Repeats Itself" \
  --type chart \
  --width 16 --height 12 \
  --config '{"metricId": "ESsGkF2vyX3En7TsS5t38e", "visualizationType": "pie", "monitoring": "Simulations", "aggregation": "count", "metricOutputType": "string"}'
```

### Table Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Metrics Overview" \
  --type table \
  --width 48 --height 8 \
  --config '{"metricIds": ["29BlkepvvX19ebbLDB0y6Q", "7VHk6dTjvBcuV6XYPmaeGq"], "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

### Text Widget

```bash
coval dashboards widgets create <dashboard_id> \
  --name "Dashboard Notes" \
  --type text \
  --width 48 --height 2 \
  --config '{"text": "## Q1 Agent Performance\nTracking key metrics across all simulation runs."}'
```
