---
name: list-dashboards
description: List all Coval dashboards with filtering and pagination. Use when user says "list dashboards", "show my dashboards", "find a dashboard", or "what dashboards do I have".
argument-hint: ""
---

# List Coval Dashboards

List all available dashboards.

## Instructions

### Step 1: Verify CLI Authentication

```bash
coval whoami
```

### Step 2: List Dashboards

```bash
coval dashboards list
```

For JSON output with full details:

```bash
coval dashboards list --format json
```

### Step 3: Filter or Page (Optional)

```bash
# Custom page size
coval dashboards list --page-size 100

# Sort by name
coval dashboards list --order-by display_name
```

### Step 4: Present Results

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
