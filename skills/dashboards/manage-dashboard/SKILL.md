---
name: manage-dashboard
description: Get, update, or delete a Coval dashboard. Use when user says "get dashboard", "rename dashboard", "delete dashboard", "update dashboard", or "show dashboard details".
argument-hint: "[dashboard-id]"
---

# Manage Coval Dashboard

Manage dashboard `$ARGUMENTS`.

## Instructions

### Step 1: Verify CLI Authentication

```bash
coval whoami
```

If no dashboard ID provided, list available dashboards:

```bash
coval dashboards list
```

### Get Dashboard Details

```bash
coval dashboards get <dashboard_id>
```

For JSON output:

```bash
coval dashboards get <dashboard_id> --format json
```

Also list its widgets:

```bash
coval dashboards widgets list <dashboard_id>
```

### Update Dashboard Name

```bash
coval dashboards update <dashboard_id> --name "New Dashboard Name"
```

### Delete Dashboard

```bash
coval dashboards delete <dashboard_id>
```

CRITICAL: This deletes the dashboard and all its widgets. Confirm with the user before proceeding.

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--name` | New dashboard name (update only) | — |
| `--format` | Output format | `table` |

## Troubleshooting

### Dashboard not found
Cause: Invalid dashboard ID.
Solution: Run `coval dashboards list` to find the correct ID.
