---
name: manage-dashboard
description: Get, update, or delete a Coval dashboard. Use when user wants to view, rename, or remove a dashboard.
argument-hint: "[dashboard-id]"
---

# Manage Coval Dashboard

Manage dashboard `$ARGUMENTS`.

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

**Warning:** This deletes the dashboard and all its widgets. Confirm with the user before proceeding.

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--name` | New dashboard name (update only) | — |
| `--format` | Output format | `table` |
