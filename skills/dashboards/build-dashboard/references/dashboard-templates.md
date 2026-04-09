# Dashboard Layout Guide

Guidelines for composing dashboards. All layouts use the **48-column** grid system. These are **starting points, not templates** — adapt the layout to the user's actual metrics and purpose.

## Layout Principles

- **Max 8-10 widgets** per dashboard unless the user requests more
- **Text widgets**: Section separators. Fixed 2h tall. Width: full (48), half (24), or third (16). **Markdown does not render** — plain text only.
- **Recent data only**: Widgets display data from the last 7 days. Warn users if data is older.
- **Table widgets**: Always full-width (48 cols).
- **Chart widgets**: Halves (24), thirds (16), or **fourths (12)** when you have many metrics.
- **Statistic widgets**: Only when data is sparse (< 2 runs close together). Otherwise use time series.
- **Latency always included**: Every dashboard should show Latency somewhere.
- **Group by theme**: Organize into meaningful sections.
- **Improve = rebuild**: When improving an existing dashboard, delete all widgets and recreate from scratch. Don't append.

## Visualization Selection Guide

**FAVOR TIME SERIES.** The default for most metrics should show change over time, not a single number or pie chart.

| Metric Type | Default Viz | Config | Size | Notes |
|-------------|-------------|--------|------|-------|
| **Float** (latency, duration, count) | `line` | `aggregation: "avg", metricOutputType: "float"` | 24×8 or 12×8 | **Default for all floats.** |
| **Binary YES/NO** (resolution, tone) | `bar` | `aggregation: "count", stacked: true, showAsPercentage: true, metricOutputType: "string"` | 24×8 or 12×8 | **100% stacked bar showing YES/NO ratio over time.** |
| **Categorical string** (end reason) | `bar` | `aggregation: "count", metricOutputType: "string"` | 24×8 | Category distribution. |
| **Float, sparse data** | `statistic` | `aggregation: "avg", metricOutputType: "float"` | 16×12 | Only when < 2 runs close together. |
| **Float, variance focus** | `histogram` | `aggregation: "avg", metricOutputType: "float"` | 16×12 | Only if user asks about distribution. |
| **Multiple metrics** | `table` | `aggregation: "success", groupBy: "agent"` | 48×8 | Always last widget. |

**NEVER use pie charts** unless:
- The metric is truly categorical (5+ distinct string values)
- AND the user explicitly asks for pie

Binary YES/NO metrics get **stacked bar charts**, not pie charts.

## Data Density Rules

Check run timestamps before choosing viz types:

| Data Density | Use | Avoid |
|-------------|-----|-------|
| 2+ runs within 4 hours of each other, or 5+ runs in 7 days | Line charts, bar charts (time series) | Statistics |
| Sparse isolated runs (< 2 in same 4h bucket) | Statistics | Line/bar charts (will look broken with 1 data point) |

## Row Width Options

| Widgets per Row | Widths | Total |
|----------------|--------|-------|
| 1 widget | 48 | 48 |
| 2 widgets | 24 + 24 | 48 |
| 3 widgets | 16 + 16 + 16 | 48 |
| 4 widgets | 12 + 12 + 12 + 12 | 48 |

Use **fourths (12)** when you have 4+ similar metrics in a section. Don't force everything into halves.

## Metric Grouping Guide

| Section Name | Metrics That Belong |
|-------------|---------------------|
| Response Performance | Latency, Time to First Byte, Audio Duration |
| Conversation Quality | Turn Count, Words Per Message, Agent Repeats Itself, Speech Tempo |
| Compliance & Quality | Issue Resolution, Caller Identity Verification, Professional Tone |
| Reliability | Agent Fails to Respond, End Reason, Transcription Error |
| Audio Quality | Background Noise, Music Detection, Natural Tone |

## Example Compositions

### Time series dashboard (enough data, 8 metrics)

```
┌─────────────────────────────────────────────────┐
│  Response Performance                    (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Line Chart            │  Line Chart            │  24+24=48, 8h
│  (Latency)             │  (Audio Duration)      │
├─────────────────────────────────────────────────┤
│  Compliance & Quality                    (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Stacked Bar           │  Stacked Bar           │  24+24=48, 8h
│  (Issue Resolution)    │  (Identity Verified?)  │
├─────────────────────────────────────────────────┤
│  Conversation Quality                    (text)  │  48col, 2h
├────────┬────────┬────────┬──────────────────────┤
│  Line  │  Line  │  Line  │  Line               │  12+12+12+12=48, 8h
│  (Turns)│ (Words)│ (Rpts) │  (Tone)             │
├─────────────────────────────────────────────────┤
│  Summary Table (all metrics)                     │  48col, 8h
└─────────────────────────────────────────────────┘
```
10 widgets. Line charts for floats, stacked bars for binary. Fourths row for 4 metrics.

### Sparse data dashboard (few runs, 5 metrics)

```
┌─────────────────────────────────────────────────┐
│  Overview                                (text)  │  48col, 2h
├───────────────┬───────────────┬─────────────────┤
│  Statistic    │  Statistic    │  Statistic      │  16+16+16=48, 12h
│  (Latency)    │  (Turn Count) │  (Audio Dur.)   │
├─────────────────────────────────────────────────┤
│  Summary Table (all metrics)                     │  48col, 8h
└─────────────────────────────────────────────────┘
```
5 widgets. Statistics because not enough data for time series.

## Widget Config Reference

### Chart config
```json
{
  "metricId": "<metric_id>",
  "visualizationType": "line|bar|statistic|histogram|area|top-list",
  "monitoring": "Simulations|Monitoring",
  "aggregation": "avg|sum|count|max|min|success",
  "metricOutputType": "float|string"
}
```

Optional: `precision`, `units`, `showAsPercentage`, `bucketInterval`, `groupBy`, `filters`

### Table config
```json
{
  "monitoring": "Simulations",
  "aggregation": "success",
  "groupBy": "agent",
  "filters": {
    "metricIds": ["<id1>", "<id2>"]
  }
}
```

- `aggregation: "success"` handles both float and string metrics.
- `groupBy: "agent"` splits rows by agent.
- Metric IDs go in `filters.metricIds`, not top-level.

### Text config
```json
{"text": "Section Title Here"}
```

## Grid Position Tracking

| Widget Type | Typical Height |
|-------------|----------------|
| text | 2 |
| statistic | 12 |
| line/bar/area/histogram | 8 |
| table | 8 |
