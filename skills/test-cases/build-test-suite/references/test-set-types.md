# Test Set Types

Each test set has a type that determines how test cases are interpreted and delivered to the agent during simulation.

## Types

### SCENARIO

Natural language task descriptions. The persona receives the scenario as instructions for what to accomplish during the call.

- **Best for**: Testing agent behavior against diverse situations
- **When to use**: Most use cases — this is the recommended default for new test sets
- **Example input**: "You are a customer calling to dispute a charge of $45.99 on your credit card from last Tuesday. You have your account number ready."

### TRANSCRIPT

OpenAI-format conversation replay. The conversation is replayed turn-by-turn against the agent.

- **Best for**: Regression testing with known-good conversations, testing specific conversation flows
- **When to use**: When you have existing conversations you want to replay exactly, or when testing specific multi-turn patterns
- **Example input**: `[{"role": "user", "content": "Hi, I need help with my order"}, {"role": "assistant", "content": "..."}, ...]`

### AUDIO

Pre-recorded audio files. The audio is played to the agent during simulation.

- **Best for**: Testing with real customer recordings, accent/dialect testing, stress testing with noisy audio
- **When to use**: When you have real call recordings you want to use as test inputs
- **Example input**: Path or URL to an audio file

### IVR

Interactive Voice Response navigation trees. Tests IVR menu navigation and routing.

- **Best for**: Testing IVR menu navigation and routing logic
- **When to use**: When your agent includes an IVR system and you want to test menu paths
- **Example input**: IVR tree definition with expected navigation paths

### SCRIPT

Ordered lines the persona speaks verbatim, one at a time.

- **Best for**: Exact phrase testing, compliance script verification
- **When to use**: When the persona must say specific phrases in a specific order (e.g., regulatory disclosures, scripted greetings)
- **Example input**: Line-by-line script the persona will read

### DEFAULT

Legacy type from earlier versions of the platform.

- **Best for**: N/A — prefer SCENARIO for new test sets
- **When to use**: Only when working with existing test sets that use this type

## Choosing a Type

| Use Case | Recommended Type |
|----------|-----------------|
| General agent testing | SCENARIO |
| Regression testing known conversations | TRANSCRIPT |
| Testing with real recordings | AUDIO |
| IVR menu testing | IVR |
| Compliance script verification | SCRIPT |
| Existing legacy test sets | DEFAULT |

When in doubt, choose **SCENARIO**. It is the most flexible and covers the majority of evaluation needs.
