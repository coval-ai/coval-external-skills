# Dashboard Skills

Skills for creating and managing Coval dashboards and widgets.

## Available Skills

| Skill | Description |
|-------|-------------|
| [create-dashboard](./create-dashboard/) | Create a new dashboard and populate it with widgets |
| [list-dashboards](./list-dashboards/) | List all dashboards |
| [manage-dashboard](./manage-dashboard/) | Get, update, or delete a dashboard |
| [add-widget](./add-widget/) | Add a widget to a dashboard |
| [manage-widgets](./manage-widgets/) | List, update, or delete widgets in a dashboard |

## Overview

Dashboards provide customizable views for visualizing agent evaluation metrics. Each dashboard contains widgets — charts, tables, or text blocks — arranged on a 48-column grid.

## Grid Layout

The dashboard uses a **48-column** grid system:

| Constraint | Value |
|------------|-------|
| Total columns | 48 |
| Global min width | 4 |
| Global max width | 48 |
| Global min height | 8 |
| Global max height | 30 |
| Default width | 12 |
| Default height | 8 |

### Widget-Type Sizing

| Widget Type | Min Width | Min Height | Max Height | Default Width | Default Height | Notes |
|-------------|-----------|------------|------------|---------------|----------------|-------|
| `chart` | 12 | 8 | 30 | 12 | 8 | — |
| `chart` (statistic) | 10 | 12 | 30 | 12 | 12 | Max width: 24 |
| `table` | 4 | 8 | 30 | 48 (full width) | 8 | Tables default to full width |
| `text` | 12 | 2 | 2 | 16 | 2 | Fixed height of 2 rows |

## CLI Commands

```bash
# Dashboards
coval dashboards list                              # List all dashboards
coval dashboards create --name "My Dashboard"      # Create a dashboard
coval dashboards get <dashboard_id>                # Get dashboard details
coval dashboards update <dashboard_id> --name "X"  # Rename dashboard
coval dashboards delete <dashboard_id>             # Delete dashboard

# Widgets
coval dashboards widgets list <dashboard_id>                          # List widgets
coval dashboards widgets create <dashboard_id> --name "X" --type chart --config '{...}'  # Add widget
coval dashboards widgets get <dashboard_id> <widget_id>               # Get widget
coval dashboards widgets update <dashboard_id> <widget_id> --name "X" # Update widget
coval dashboards widgets delete <dashboard_id> <widget_id>            # Delete widget
```
