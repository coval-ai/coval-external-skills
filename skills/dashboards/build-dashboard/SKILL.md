---
name: build-dashboard
description: Build or improve a Coval dashboard with metric visualizations backed by real data. Creates new dashboards from scratch or enhances existing ones by analyzing usage patterns, metric frequency, and gaps. Use when user says "create a dashboard", "build a dashboard", "improve my dashboard", "add widgets", "visualize my metrics", "make a performance dashboard", or "dashboard for my runs".
argument-hint: "[dashboard-purpose-or-name]"
---

# Setup Coval Dashboard

Build a data-driven dashboard for `$ARGUMENTS`. This skill analyzes the user's existing runs and metrics to create a dashboard populated with real data — never an empty shell.

## Phase 0: Preflight + Usage Analysis

### Step 1: Check authentication

```bash
coval whoami
```

If not authenticated, guide the user:
```bash
coval login
```
This prompts for an API key. Get one at https://app.coval.dev/settings (Organization > Manage > API Keys).

If the user doesn't have a Coval account, direct them to https://coval.dev to sign up.

### Step 2: Inventory resources

Run these in parallel:

```bash
coval dashboards list --format json
coval metrics list --include-builtin --format json
coval agents list --format json
coval runs list --format json --page-size 50
```

If dashboards exist, ask: "You have existing dashboards. Modify one or create new?"

### Step 3: Analyze usage patterns

**This is the critical intelligence step.** Determine the data source automatically:

1. **Count runs by type**: Check each run for the presence of `test_set_id`.
   - Runs **with** `test_set_id` → Simulation runs (evaluation test runs)
   - Runs **without** `test_set_id` → Monitoring runs (live conversation submissions)
   - Note: Some runs may also have an `is_monitoring` field, but the primary signal is `test_set_id` presence.

2. **Decision logic** (do NOT ask the user unless ambiguous):
   - Mostly simulation runs → data source is `Simulations`
   - Mostly monitoring runs → data source is `Monitoring`
   - Roughly equal → ask user which they prefer
   - **Human review**: Only if the user explicitly mentions it. Do not suggest.

3. **No recent data scenario — STOP and ask before proceeding.**

   Dashboard widgets only display data from the **last 7 days** (rolling window). Data older than 7 days will NOT appear in any widget, regardless of how many runs exist historically.

   Filter runs by `create_time` and only consider runs from the last 7 days. Then check those runs for **successful simulations with actual metric data** — a run with status COMPLETED but all failed simulations is useless for a dashboard.

   To verify, fetch simulations for each recent run and check that at least some have `status: "COMPLETED"` with non-null metric values. A run where every simulation failed = no data.

   **If there are no runs with successful simulations in the last 7 days, DO NOT create the dashboard yet.** Instead:

   Tell the user:
   > "You don't have any recent evaluation data (last 7 days). I need to run some evaluations first so the dashboard has real data to display."

   Then invoke `/quick-eval` with these **minimum requirements for a useful dashboard**:
   - **At least 5 simulations** (use `--iterations` or pick a test set with 5+ test cases)
   - **At least 5 metrics** including **Latency** (always required — find its ID from the builtin metrics list)
   - **Confirm agent and test set with the user** before launching (unless there's only 1 agent — then auto-select)

   **STOP this skill. Invoke `/quick-eval`** with the above parameters. Wait for the evaluation to complete and produce metric data. Only then resume `/setup-dashboard`.

   - If there are **no runs at all**: Also ask whether they want a Simulations or Monitoring dashboard before invoking `/quick-eval`.
   - If the user explicitly says they don't want to run evals: **Do NOT create the dashboard.** Tell them to come back when they have data. An empty dashboard is a waste — never create one.

   **There is no "proceed anyway" path.** No data = no dashboard. This is non-negotiable.

   **Human review**: Only if the user explicitly mentions it. Do not suggest.

### Step 4: Identify top metrics by frequency

**Only consider runs from the last 7 days.** If no recent runs exist and `/quick-eval` was just run, use that run's data.

For the most recent completed runs (up to 10), fetch simulation metrics:

```bash
coval simulations list --run-id <run_id> --format json --page-size 5
coval simulations metrics <simulation_id> --format json
```

Build a frequency map: count how many times each `metric_id` appears with `status: "COMPLETED"` and non-null `value` across simulations. **Sort by frequency descending.**

**Latency is mandatory.** Always include Latency (`29BlkepvvX19ebbLDB0y6Q` or find by `metric_name: "Latency"`) in the dashboard regardless of its frequency ranking. If it's not in the top metrics, add it.

Cross-reference metric IDs with the metrics inventory to get display names and output types.

If a metric has never produced data (all `status: "FAILED"` or `value: null`), deprioritize it — place it lower or omit it.

**Present the frequency map to the user** before building the layout:

```
Metric frequency (last 7 days):

  Metric                  | Appearances | Status
  ────────────────────────|─────────────|────────
  Latency                 | 10/10       | ✓ data
  Turn Count              | 10/10       | ✓ data
  Words Per Message       | 8/10        | ✓ data
  Agent Repeats Itself    | 5/10        | ✓ data
  Background Noise        | 0/10        | ✗ no data (omitting)
```

Ask: **"These are the metrics with data. Use all of them, or adjust?"**

> **Note:** Some simulations may return errors when fetching metrics (e.g., audio simulations). Skip those gracefully and continue with the next simulation.

## Phase 1: Dashboard Planning

### Step 1: Select agent focus

If there is **only 1 agent**, auto-select it and tell the user.

If there are **multiple agents**, ask: **"Which agent should this dashboard focus on?"**
- Present agents as a numbered list, highlighting voice agents (they have richer metrics)
- Allow "all agents" for a cross-agent view

### Step 2: Determine layout

Based on the data source and metric count, choose a layout. A good dashboard has **at most 8 widgets** unless the user specifically requests more or is adding a widget to an existing dashboard.

**Layout principles:**
- **Text widgets** separate sections by utility. They are fixed at 2 rows tall and only vary in width: full-width (48), half (24), or thirds (16). **Markdown does not render in text widgets — use plain text only.**
- **Table widgets** should be full-width (48 cols).
- **Chart widgets** (line, bar, area, pie, histogram) should be half-width (24 cols) or thirds (16 cols).
- **Statistic widgets** should be thirds (16 cols) or halves (24 cols).

### Step 3: Build the widget list

**This is where you use judgment — not a template.** The layout should be unique to the user's data, metrics, and purpose. Do not produce the same dashboard every time.

**Hard rules (non-negotiable):**
- Text widget section headers are **REQUIRED** to separate visual sections. Without them the dashboard is a wall of charts.
- Latency must always appear somewhere (statistic, chart, or table).
- Max 8 widgets unless user asks for more.
- All rows must sum to 48 columns.

**Visualization selection — match the metric to the right chart type:**

| Metric Output Type | Good Visualizations | When to Use |
|---------------------|---------------------|-------------|
| Float (latency, duration, count) | `statistic` | Single KPI number — use for the 2-3 most important metrics |
| Float (latency, duration) | `line` | Trends over time — use when the user cares about trajectory |
| Float (scores, counts) | `bar` | Comparing across runs or categories |
| Float (latency, duration) | `histogram` | Distribution — use when variance matters (e.g., "is latency consistent or spiky?") |
| String/Boolean (resolution, sentiment) | `pie` | Proportions — use for yes/no or categorical outcomes |
| String/Boolean (resolution, sentiment) | `bar` | Comparing categories across runs |
| String (end reason, sentiment) | `top-list` | Ranking — use for "what are the most common outcomes?" |

**Think about what story the dashboard tells.** A performance overview is different from a quality audit is different from a trend analysis:

- **Performance overview**: Lead with Latency statistic + 2 other KPIs. Add a trend line for the primary metric. End with a summary table.
- **Quality audit**: Lead with pass/fail pie charts for binary metrics. Add statistics for failure rates. Table showing per-test-case breakdown.
- **Trend analysis**: All line/area charts. Show how metrics change over time. Statistics are less useful here.
- **Live monitoring**: Real-time statistics at the top. Area chart for volume trends. Top-list for common issues.

**Compose sections based on what metrics you have:**

For each group of related metrics, create a section:
1. **Text header** describing the section (e.g., "Response Performance", "Conversation Quality", "Audio Metrics")
2. **1-3 widgets** visualizing those metrics with appropriate chart types
3. Repeat for the next group

Group metrics by theme, not arbitrarily:
- Latency + Audio Duration + Time to First Byte → "Response Performance"
- Turn Count + Words Per Message + Agent Repeats Itself → "Conversation Quality"
- Sentiment + Call Resolution + Custom LLM Judge → "Outcome Analysis"
- Agent Fails to Respond + End Reason → "Reliability"

If you only have 2-3 metrics, don't force multiple sections — one section header + widgets + table is fine.

### Step 4: Present and confirm

**You MUST show the layout as an ASCII box-drawing mockup** — not a markdown table, not a bullet list, not a description. Build the mockup from your actual planned widgets. Example format:

```
Dashboard: "<name>" (data: <Simulations|Monitoring>)

┌─────────────────────────────────────────────────┐
│  Response Performance                    (text)  │  48col, 2h
├───────────────┬───────────────┬─────────────────┤
│  Statistic    │  Statistic    │  Histogram      │  16+16+16=48, 12h
│  (Latency)    │  (Audio Dur.) │  (Latency dist) │
├─────────────────────────────────────────────────┤
│  Conversation Quality                    (text)  │  48col, 2h
├────────────────────────┬────────────────────────┤
│  Line Chart            │  Pie Chart             │  24+24=48, 8h
│  (Turn Count trend)    │  (Agent Repeats?)      │
├─────────────────────────────────────────────────┤
│  Summary Table (all metrics)                     │  48col, 8h
└─────────────────────────────────────────────────┘

Widgets: 8 total
```

The mockup above is an **example** — your layout should reflect the actual metrics and groupings you chose, not this exact structure.

Ask: **"Does this layout look right? (yes / customize)"**

If customize:
- Allow swapping visualization types (e.g., line → histogram, statistic → pie)
- Allow adding/removing widgets (warn if going above 8)
- Allow reordering sections or metrics
- Allow changing section groupings

## Phase 2: Create Dashboard + Widgets

### Step 1: Create the dashboard

```bash
coval dashboards create --name "<dashboard_name>" --format json
```

Capture `dashboard_id` from the JSON response.

### Step 2: Create widgets row by row

Create widgets top to bottom, left to right. Use explicit `--grid-x` and `--grid-y` positioning to ensure correct layout.

#### Text widgets (section headers)

```bash
coval dashboards widgets create <dashboard_id> \
  --name "<section_title>" \
  --type text \
  --grid-w 48 --grid-h 2 \
  --grid-x 0 --grid-y <row_y> \
  --config '{"text": "<section_title>"}'
```

Text widgets are always 2 rows tall. Width options: 48 (full), 24 (half), 16 (third). **No markdown — plain text only.**

#### Chart widgets (line, bar, area, statistic, pie, histogram, top-list)

```bash
coval dashboards widgets create <dashboard_id> \
  --name "<widget_name>" \
  --type chart \
  --grid-w <cols> --grid-h <rows> \
  --grid-x <x> --grid-y <y> \
  --config '{"metricId": "<metric_id>", "visualizationType": "<viz_type>", "monitoring": "<Simulations|Monitoring>", "aggregation": "<agg>", "metricOutputType": "<float|string>"}'
```

Width options: 48 (full), 24 (half), 16 (third). Aggregation values: `sum`, `count`, `avg`, `max`, `min`, `success`.

Optional config: `precision`, `units`, `showAsPercentage`, `bucketInterval`, `groupBy`, `filters`

#### Table widgets

```bash
coval dashboards widgets create <dashboard_id> \
  --name "<widget_name>" \
  --type table \
  --grid-w 48 --grid-h 8 \
  --grid-x 0 --grid-y <row_y> \
  --config '{"monitoring": "<Simulations|Monitoring>", "aggregation": "success", "groupBy": "agent", "filters": {"metricIds": ["<id1>", "<id2>"]}}'
```

**Table widget rules:**
- Always full-width (48 cols)
- Always use `aggregation: "success"` — this handles both float and string metrics correctly. Using `"avg"` breaks string metrics.
- Always use `groupBy: "agent"` — splits rows by agent so you can compare performance across agents.
- Put metric IDs in `filters.metricIds` (NOT top-level `metricIds`) — the frontend reads `filters.metricIds` first.

### Grid position tracking

Track `grid_y` as you create rows:
- Row 0: text header (h=2) → next y = 2
- Row 2: statistics (h=12) → next y = 14
- Row 14: text header (h=2) → next y = 16
- Row 16: charts (h=8) → next y = 24
- Row 24: table (h=8) → next y = 32

## Phase 3: Verify + Fix Layout

### Step 1: Fetch actual widget state

```bash
coval dashboards widgets list <dashboard_id> --format json
```

### Step 2: Verify and show evidence

**Show the user the raw widget list output** as proof of correct layout. Then verify:

- Widget sizes (`grid_w`, `grid_h`) respect type minimums (chart ≥ 12w×8h, statistic ≥ 10w×12h, table ≥ 4w×8h, text ≥ 12w×2h)
- Each row's widgets should sum to exactly **48 columns** wide
- No unexpected size adjustments from the server

Present the verification result:

```
Layout verified:
  ✓ Row 0: text 48w = 48 ✓
  ✓ Row 2: stat 16w + stat 16w + stat 16w = 48 ✓
  ✓ Row 14: text 48w = 48 ✓
  ✓ Row 16: chart 24w + chart 24w = 48 ✓
  ✓ Row 24: table 48w = 48 ✓
  ✓ All widget sizes meet type minimums
  ✓ No server-side adjustments detected
```

> **Note:** When you set `--grid-x` and `--grid-y` during creation, the positions are persisted and returned in the response. Always set explicit positions to ensure a clean layout.

### Step 3: Fix any issues

```bash
coval dashboards widgets update <dashboard_id> <widget_id> --grid-x <x> --grid-y <y> --grid-w <w> --grid-h <h>
```

## Phase 4: Summary

Once all widgets are created and verified, immediately tell the user their dashboard is ready and give them the link to open it:

```
Your dashboard is ready!

  Name:       <dashboard_name>
  Widgets:    <count>
  Data:       <Simulations|Monitoring>

  Open it here: https://app.coval.dev/dashboards/<dashboard_id>

  Layout:
  | Widget              | Type      | Size   | Metric              |
  |---------------------|-----------|--------|---------------------|
  | Key Metrics         | text      | 48×2   | —                   |
  | Latency             | statistic | 16×12  | Latency             |
  | <top metric>        | statistic | 16×12  | <metric name>       |
  | ...                 | ...       | ...    | ...                 |
```

The dashboard link is the most important output — make it prominent so the user can open it in their browser right away.

**Always suggest next steps:**
- Run more evaluations to enrich the data: `/quick-eval`
- Add more widgets later: `coval dashboards widgets create`
- Set up scheduled runs for continuous data: `coval scheduled-runs create`
- Configure more metrics: `/configure-metrics`
