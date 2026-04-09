# Test Case Skills

Skills for building and managing Coval evaluation test cases.

## Available Skills

| Skill | Description |
|-------|-------------|
| [build-test-suite](./build-test-suite/) | Interactive guide to build a test suite with scenarios and expected behaviors |
| [huggingface-import](./huggingface-import/) | Import datasets from HuggingFace and convert to Coval test sets |

## Overview

Test cases define specific scenarios for evaluating agent performance. Each test case contains:

- **input**: The prompt or question to send to the agent
- **metadata**: Optional JSON with additional context (IDs, categories, source info)

Test cases are organized into **test sets** - collections grouped by category, evaluation type, or purpose.

## Coval Structure

```
Test Set (e.g., "MT-Bench Reasoning")
├── Test Case 1: "What is the meaning of life?"
├── Test Case 2: "Explain the trolley problem..."
└── Test Case 3: ...
```

## CSV Format

Coval accepts test cases as CSV files:

```csv
input,metadata
"Your question here","{""question_id"": 1, ""category"": ""reasoning""}"
```

Requirements:
- `input` column first
- Proper quote escaping
- `metadata` as valid JSON string
