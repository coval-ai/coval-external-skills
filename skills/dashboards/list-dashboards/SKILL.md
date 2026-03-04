---
name: list-dashboards
description: List all Coval dashboards. Use when user wants to see available dashboards or find a dashboard ID.
argument-hint: ""
---

# List Coval Dashboards

List all available dashboards.

## Prerequisites

Ensure the Coval CLI is installed and authenticated:
```bash
coval whoami
```

## Workflow

### Step 1: List Dashboards

```bash
coval dashboards list
```

For JSON output with full details:

```bash
coval dashboards list --format json
```

### Step 2: Filter or Page (Optional)

```bash
# Custom page size
coval dashboards list --page-size 100

# Sort by name
coval dashboards list --order-by display_name
```

### Step 3: Present Results

Show the user:
- Dashboard ID
- Dashboard name
- Created/updated timestamps

Offer follow-up actions:
- View a specific dashboard: `coval dashboards get <id>`
- List widgets in a dashboard: `coval dashboards widgets list <id>`
- Create a new dashboard: `coval dashboards create --name "Name"`

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--filter` | AIP-160 filter expression | — |
| `--page-size` | Results per page | 50 |
| `--order-by` | Sort order | — |
| `--format` | Output format | `table` |
