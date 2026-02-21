# Run Skills

Skills for launching and monitoring Coval evaluation runs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [launch-run](./launch-run/) | Launch an evaluation run against an agent |
| [watch-run](./watch-run/) | Monitor run progress with live updates |
| [quick-eval](./quick-eval/) | Full workflow: launch, watch, and summarize results |

## Overview

Runs are the core evaluation unit in Coval. A run executes test cases against an agent using a simulated persona and collects results as simulations.

## CLI Commands

```bash
coval runs list                    # List all runs
coval runs get <run_id>            # Get run details
coval runs launch ...              # Start a new run
coval runs watch <run_id>          # Monitor progress
coval runs delete <run_id>         # Delete a run
```
