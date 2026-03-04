---
name: manage-widgets
description: List, get, update, or delete widgets in a Coval dashboard. Use when user wants to view, modify, or remove dashboard widgets.
argument-hint: "[dashboard-id]"
---

# Manage Dashboard Widgets

Manage widgets in dashboard `$ARGUMENTS`.

## Prerequisites

Ensure the Coval CLI is installed and authenticated:
```bash
coval whoami
```

If no dashboard ID provided, list available dashboards:

```bash
coval dashboards list
```

## Operations

### List Widgets

```bash
coval dashboards widgets list <dashboard_id>
```

For JSON output with full config and grid positions:

```bash
coval dashboards widgets list <dashboard_id> --format json
```

### Get Widget Details

```bash
coval dashboards widgets get <dashboard_id> <widget_id>
```

For JSON output:

```bash
coval dashboards widgets get <dashboard_id> <widget_id> --format json
```

### Update Widget

Update name, type, size, or config:

```bash
# Rename
coval dashboards widgets update <dashboard_id> <widget_id> --name "New Name"

# Resize
coval dashboards widgets update <dashboard_id> <widget_id> --width 24 --height 12

# Update config
coval dashboards widgets update <dashboard_id> <widget_id> \
  --config '{"metricId": "...", "visualizationType": "bar", "monitoring": "Simulations", "aggregation": "avg", "metricOutputType": "float"}'
```

**Important:** After updating, check the **returned** values — the server may adjust dimensions to enforce widget-type minimums.

### Delete Widget

```bash
coval dashboards widgets delete <dashboard_id> <widget_id>
```

Confirm with the user before deleting.

### Verify Layout

After any changes, verify no gaps in the grid:

```bash
coval dashboards widgets list <dashboard_id> --format json
```

Check that:
- Each row's widgets sum to 48 columns
- No vertical gaps between rows
- Sizes respect type minimums

## Grid Constraints

| Widget Type | Min Width | Min Height | Max Height | Notes |
|-------------|-----------|------------|------------|-------|
| `chart` | 12 | 8 | 30 | — |
| `chart` (statistic) | 10 | 12 | 30 | Max width: 24 |
| `table` | 4 | 8 | 30 | Defaults to full width (48) |
| `text` | 12 | 2 | 2 | Fixed height |

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--name` | Widget display name | — |
| `--type` | Widget type (`chart`, `table`, `text`) | — |
| `--config` | JSON config string | — |
| `--width` | Grid width in columns | — |
| `--height` | Grid height in rows | — |
| `--page-size` | Results per page (list only) | 50 |
| `--format` | Output format | `table` |
