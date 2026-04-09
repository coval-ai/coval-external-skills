# Dashboard Layout Guide

Guidelines for composing dashboards. All layouts use the **48-column** grid system. These are **starting points, not templates** — adapt the layout to the user's actual metrics and purpose.

## Layout Principles

- **Max 8 widgets** per dashboard unless the user requests more
- **Text widgets**: Section separators. Fixed 2h tall. Width: full (48), half (24), or third (16). **Markdown does not render** — plain text only.
- **Recent data only**: Widgets display data from the last 7 days. Warn users if data is older.
- **Table widgets**: Always full-width (48 cols).
- **Chart widgets**: Half-width (24) or thirds (16).
- **Statistic widgets**: Thirds (16) or halves (24).
- **Latency always included**: Every dashboard should show Latency somewhere.
- **Group by theme**: Don't just list metrics — organize them into meaningful sections.

## Visualization Selection Guide

Pick the visualization that tells the right story for each metric:

| Metric Type | Visualization | When to Use | Size |
|-------------|---------------|-------------|------|
| Float KPI (latency, duration) | `statistic` | Show the current value prominently | 16×12 |
| Float over time (latency trend) | `line` | Show trajectory/direction | 24×8 |
| Float over time (volume) | `area` | Show cumulative volume | 24×8 or 32×8 |
| Float variance (latency spread) | `histogram` | Show distribution — is it consistent or spiky? | 16×12 or 24×8 |
| Float comparison (across runs) | `bar` | Compare values side by side | 24×8 |
| Boolean/String (yes/no, pass/fail) | `pie` | Show proportions of outcomes | 16×12 |
| String categories (sentiment, end reason) | `bar` | Compare category frequencies | 24×8 |
| String ranking (top issues) | `top-list` | Show most common values | 16×8 |
| Multiple metrics | `table` | Compare all metrics at once | 48×8 |

**Don't default to `statistic` + `line` for everything.** A boolean metric like "Agent Repeats Itself" is better as a pie chart (YES/NO split) than a statistic. A metric like Latency is better as a histogram if the user cares about consistency.

## Metric Grouping Guide

Group metrics into sections by what they measure, not alphabetically:

| Section Name | Metrics That Belong |
|-------------|---------------------|
| Response Performance | Latency, Time to First Byte, Audio Duration |
| Conversation Quality | Turn Count, Words Per Message, Agent Repeats Itself, Speech Tempo |
| Outcome Analysis | Sentiment, Call Resolution, Custom LLM Judge metrics |
| Reliability | Agent Fails to Respond, End Reason, Transcription Error |
| Audio Quality | Background Noise, Music Detection, Natural Tone |

Not every dashboard needs all sections. Use only the sections relevant to the metrics that have data.

## Example Compositions

### Performance-focused (voice agent, 7 metrics)

```
┌─────────────────────────────────────────────────┐
│  Response Performance                    (text)  │  48col, 2h
├───────────────┬───────────────┬─────────────────┤
│  Statistic    │  Histogram    │  Statistic      │  16+16+16=48, 12h
│  (Latency)    │  (Latency)    │  (Audio Dur.)   │
├─────────────────────────────────────────────────┤
│  Conversation Quality                    (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Line Chart            │  Pie Chart             │  24+24=48, 8h
│  (Turn Count)          │  (Agent Repeats?)      │
├─────────────────────────────────────────────────┤
│  All Metrics                             (table) │  48col, 8h
└─────────────────────────────────────────────────┘
```
8 widgets. Mix of statistic, histogram, line, pie, table.

### Quality audit (chat agent, 5 metrics)

```
┌─────────────────────────────────────────────────┐
│  Outcome Analysis                        (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Pie Chart             │  Pie Chart             │  24+24=48, 12h
│  (Call Resolution)     │  (Sentiment)           │
├───────────────┬───────────────┬─────────────────┤
│  Statistic    │  Statistic    │  Statistic      │  16+16+16=48, 12h
│  (Latency)    │  (Turn Count) │  (Words/Msg)    │
├─────────────────────────────────────────────────┤
│  All Metrics                             (table) │  48col, 8h
└─────────────────────────────────────────────────┘
```
7 widgets. Leads with outcomes (pie), then supporting KPIs.

### Trend analysis (monitoring, 4 metrics)

```
┌─────────────────────────────────────────────────┐
│  Trends                                  (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Area Chart            │  Area Chart            │  24+24=48, 8h
│  (Latency)             │  (Turn Count)          │
├────────────────────────┬────────────────────────┤
│  Line Chart            │  Top List              │  24+24=48, 8h
│  (Words Per Msg)       │  (End Reason)          │
├─────────────────────────────────────────────────┤
│  All Metrics                             (table) │  48col, 8h
└─────────────────────────────────────────────────┘
```
6 widgets. All charts — no statistics. Focused on change over time.

### Minimal (3 metrics only)

```
┌─────────────────────────────────────────────────┐
│  Overview                                (text)  │  48col, 2h
├───────────────┬───────────────┬─────────────────┤
│  Statistic    │  Statistic    │  Statistic      │  16+16+16=48, 12h
│  (Latency)    │  (Turn Count) │  (Resolution)   │
├─────────────────────────────────────────────────┤
│  All Metrics                             (table) │  48col, 8h
└─────────────────────────────────────────────────┘
```
5 widgets. Simple — just the essentials.

## Widget Config Reference

### Chart config (required fields)
```json
{
  "metricId": "<metric_id>",
  "visualizationType": "statistic|line|bar|area|pie|histogram|top-list",
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

**Important:**
- Use `aggregation: "success"` — handles both float and string metrics. `"avg"` breaks on string metrics.
- Use `groupBy: "agent"` — splits rows by agent for comparison.
- Put metric IDs in `filters.metricIds`, not top-level `metricIds`.

### Text config
```json
{"text": "Section Title Here"}
```

## Grid Position Tracking

When creating widgets, track `grid_y` to set explicit positions. Heights vary by widget type — accumulate as you go:

| Widget Type | Typical Height |
|-------------|----------------|
| text | 2 |
| statistic | 12 |
| line/bar/area/histogram | 8 |
| pie | 12 |
| top-list | 8 |
| table | 8 |
