---
name: manage-widgets
description: List, get, update, or delete widgets in a Coval dashboard. Use when user says "list widgets", "show widgets", "update widget", "resize widget", "delete widget", "move widget", or "edit widget config".
argument-hint: "[dashboard-id]"
---

# Manage Dashboard Widgets

Manage widgets in dashboard `$ARGUMENTS`.

## Instructions

### Step 1: Verify CLI Authentication

```bash
coval whoami
```

If no dashboard ID provided, list available dashboards:

```bash
coval dashboards list
```

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

CRITICAL: After updating, check the **returned** values — the server may adjust dimensions to enforce widget-type minimums per `references/grid-layout.md`.

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
- Sizes respect type minimums per `references/grid-layout.md`

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

## Troubleshooting

### Widget not found
Cause: Invalid widget ID or wrong dashboard ID.
Solution: Run `coval dashboards widgets list <dashboard_id>` to find the correct widget ID.

### Update didn't change dimensions
Cause: Requested dimensions were below the type's minimum.
Solution: Consult `references/grid-layout.md` for valid minimums.
