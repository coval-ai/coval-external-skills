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

### categorical

LLM classifies the conversation into one of several predefined categories.

- **Output**: STRING (one of the defined categories)
- **Config**: `prompt` — the evaluation question, `categories` — comma-separated list of valid categories (min 2, max 50)
- **Use for**: Multi-outcome classification (sentiment categories, escalation reasons, call outcomes, issue types)

```bash
coval metrics create \
  --name "Call Outcome" \
  --description "Classify the overall outcome of the call" \
  --type categorical \
  --prompt "Given the transcript, classify the call outcome into one of the following categories. Return ONLY the category name." \
  --categories "Resolved,Escalated,Abandoned,Follow-Up Required,Wrong Department" \
  --format json
```

### numerical

LLM assigns a numeric score to the conversation within a defined range.

- **Output**: FLOAT (within min-max range)
- **Config**: `prompt` — the evaluation question, `min-value` — minimum score, `max-value` — maximum score
- **Use for**: Graded assessments (1-10 quality scores, 0-100 confidence ratings)

```bash
coval metrics create \
  --name "Customer Satisfaction Score" \
  --description "Rate customer satisfaction on a 1-10 scale" \
  --type numerical \
  --prompt "Given the transcript, rate the likely customer satisfaction on a scale of 1 to 10, where 1 is extremely dissatisfied and 10 is extremely satisfied. Return ONLY the number." \
  --min-value 1 --max-value 10 \
  --format json
```

### audio-categorical

LLM classifies audio quality into predefined categories. **Voice agents only.**

- **Output**: STRING (one of the defined categories)
- **Config**: `prompt`, `categories`
- **Use for**: Audio quality grading, accent detection, noise classification

### audio-numerical

LLM assigns a numeric score to audio quality. **Voice agents only.**

- **Output**: FLOAT (within min-max range)
- **Config**: `prompt`, `min-value`, `max-value`
- **Use for**: Audio quality scoring, clarity ratings

### regex

Pattern matching on the conversation transcript.

- **Output**: BOOLEAN (match found or not)
- **Config**: `regex-pattern`, optional `role` (agent/user), `case-insensitive`, `match-mode`, `position`
- **Use for**: Checking for specific phrases, compliance language, prohibited words

```bash
coval metrics create \
  --name "Disclaimer Mentioned" \
  --description "Check if the agent read the required disclaimer" \
  --type regex \
  --regex-pattern "terms and conditions|disclaimer|legal notice" \
  --role agent \
  --case-insensitive true \
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
| Yes/no criterion from transcript | `llm-binary` |
| Classify into multiple categories | `categorical` |
| Assign a numeric score | `numerical` |
| Voice/audio quality (yes/no) | `audio-binary` |
| Voice/audio quality (categories) | `audio-categorical` |
| Voice/audio quality (score) | `audio-numerical` |
| Long silences in calls | `pause` |
| Check for specific phrases | `regex` |
| Test case expected behaviors | `composite` (built-in) |
| Response speed | `latency` (built-in) |
| Caller emotion | `sentiment` (built-in) |
| Problem resolution | `call-resolution` (built-in) |
