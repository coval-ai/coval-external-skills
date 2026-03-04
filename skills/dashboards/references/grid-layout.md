# Dashboard Grid Layout Reference

The dashboard uses a **48-column** grid system.

## Global Constraints

| Constraint | Value |
|------------|-------|
| Total columns | 48 |
| Global min width | 4 |
| Global max width | 48 |
| Global min height | 8 |
| Global max height | 30 |
| Default width | 12 |
| Default height | 8 |

## Widget-Type Sizing

| Widget Type | Min Width | Min Height | Max Height | Default Width | Default Height | Notes |
|-------------|-----------|------------|------------|---------------|----------------|-------|
| `chart` | 12 | 8 | 30 | 12 | 8 | — |
| `chart` (statistic viz) | 10 | 12 | 30 | 12 | 12 | Max width: 24 |
| `table` | 4 | 8 | 30 | 48 (full width) | 8 | Tables default to full width |
| `text` | 12 | 2 | 2 | 16 | 2 | Fixed height of 2 rows |

## Layout Rules

- Each row's widgets must sum to exactly 48 columns
- No vertical gaps between rows (one row's end_y must equal the next row's grid_y)
- Always check the **returned** grid values from the CLI/API — the server may adjust dimensions to enforce minimums

## Widget Config Reference

### Chart Config

Required fields: `metricId`, `visualizationType`, `monitoring`, `aggregation`, `metricOutputType`

| Field | Values |
|-------|--------|
| `visualizationType` | `line`, `bar`, `area`, `statistic`, `pie`, `histogram`, `top-list` |
| `monitoring` | `Monitoring` (live conversations) or `Simulations` (test runs) |
| `aggregation` | `sum`, `count`, `avg`, `max`, `min`, `success` |
| `metricOutputType` | `string` or `float` |

Optional: `bucketInterval`, `groupBy`, `precision`, `units`, `showAsPercentage`, `xAxisLabel`, `yAxisLabel`, `filters`

### Table Config

Required fields: `metricIds`, `monitoring`, `aggregation`

### Text Config

Required fields: `text` (markdown content, max 10,000 chars)
