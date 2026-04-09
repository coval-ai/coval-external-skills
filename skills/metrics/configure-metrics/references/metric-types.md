# Metric Types Reference

Coval supports several metric types for evaluating AI agents. Each type has a specific output format and configuration.

## Custom Metric Types

### llm-binary

LLM evaluates a conversation transcript against a yes/no prompt.

- **Output**: BOOLEAN (YES/NO)
- **Config**: `prompt` — the evaluation question
- **Use for**: Any custom evaluation criterion (compliance checks, accuracy, tone, task completion)
- **Most flexible type** — can evaluate virtually any aspect of agent behavior

```bash
coval metrics create \
  --name "Policy Compliance" \
  --description "Did the agent follow company policies?" \
  --type llm-binary \
  --prompt "Given the transcript, did the agent follow all company policies and procedures? Return YES if compliant. Return NO if any policy was violated." \
  --format json
```

### audio-binary

LLM evaluates audio quality against a yes/no prompt. **Voice agents only.**

- **Output**: BOOLEAN (YES/NO)
- **Config**: `prompt` — the evaluation question about audio/voice quality
- **Use for**: Tone assessment, pronunciation, speech clarity, professionalism

```bash
coval metrics create \
  --name "Professional Tone" \
  --description "Agent tone quality assessment" \
  --type audio-binary \
  --prompt "Was the agent's tone professional and appropriate throughout the call?" \
  --format json
```

### pause

Detects silence gaps in audio. **Voice agents only.**

- **Output**: FLOAT (pause duration in seconds)
- **Config**: `min_pause_duration` — threshold in seconds to flag a pause
- **Use for**: Detecting long silences that indicate processing delays or agent confusion

```bash
coval metrics create \
  --name "Long Pause Detection" \
  --description "Flags pauses longer than 3 seconds" \
  --type pause \
  --min-pause-duration 3.0 \
  --format json
```

## Built-in Metric Types

These are pre-configured in every Coval organization. No creation needed — reference by existing ID.

### composite

Evaluates expected behaviors defined on each test case.

- **Output**: FLOAT (0-1 score)
- **Config**: None — automatically scores against test case `expected_behaviors`
- **Use for**: Measuring how well the agent follows the scenario's expected behavior checklist

### latency

Measures response time between user input and agent response.

- **Output**: FLOAT (seconds)
- **Config**: None
- **Use for**: Performance monitoring, identifying slow responses

### sentiment

Analyzes the emotional trajectory of the conversation.

- **Output**: STRING (sentiment classification)
- **Config**: None
- **Use for**: Understanding caller satisfaction and emotional progression

### call-resolution

Determines whether the agent resolved the caller's issue.

- **Output**: BOOLEAN
- **Config**: None
- **Use for**: Measuring overall agent effectiveness at solving problems

## Choosing the Right Type

| I want to evaluate... | Use this type |
|----------------------|---------------|
| Any custom criterion from transcript | `llm-binary` |
| Voice/audio quality | `audio-binary` |
| Long silences in calls | `pause` |
| Test case expected behaviors | `composite` (built-in) |
| Response speed | `latency` (built-in) |
| Caller emotion | `sentiment` (built-in) |
| Problem resolution | `call-resolution` (built-in) |
