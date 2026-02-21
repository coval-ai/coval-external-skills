# Simulation Skills

Skills for analyzing and working with Coval simulation results.

## Available Skills

| Skill | Description |
|-------|-------------|
| [get-results](./get-results/) | Retrieve and analyze simulation results |
| [download-audio](./download-audio/) | Download audio recordings from voice simulations |

## Overview

Simulations are individual test executions within a run. Each simulation represents one conversation between the agent and the simulated persona.

## CLI Commands

```bash
coval simulations list                      # List all simulations
coval simulations list --run-id <run_id>    # List by run
coval simulations get <sim_id>              # Get details + transcript
coval simulations audio <sim_id>            # Get audio URL
coval simulations audio <sim_id> -o out.wav # Download audio
coval simulations delete <sim_id>           # Delete simulation
```
