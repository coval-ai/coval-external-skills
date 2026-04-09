# Metric Recommendation Engine

Maps `(agent_type, use_case, critical_requirement)` to a list of metrics to create or reference.

## Always Recommend (every evaluation)

### Composite Evaluation (built-in)
- **Action**: Find existing ID from `coval metrics list --format json`
- **How to find**: Look for a metric with `metric_name` containing "composite" or `display_name` = "Composite Evaluation"
- **Purpose**: Evaluates expected behaviors defined on each test case

### Default Built-in Metrics
These are pre-existing in every org. Find their IDs from `coval metrics list`:
- **Latency** — Time between user input and agent response
- **Call Resolution** — Did the agent resolve the issue?
- **Sentiment** — Emotional trajectory of conversation

## Use-Case Specific Custom Metrics

Create ONE custom llm-binary metric based on the use case.

### customer_support
- **Name**: Issue Resolution
- **Description**: Did the agent successfully resolve or appropriately escalate the customer's issue?
- **Prompt**: "Given the transcript of a customer support call, did the agent successfully resolve or appropriately escalate the customer's issue? Return YES if the customer's problem was addressed, solved, or properly escalated to a human. Return NO if the issue was ignored, mishandled, or the customer was left without a resolution path."

### scheduling_booking
- **Name**: Booking Accuracy
- **Description**: Did the agent correctly book, modify, or cancel the appointment as requested?
- **Prompt**: "Given the transcript, did the agent correctly book, modify, or cancel the appointment as requested by the caller? Return YES if the booking action was completed accurately with correct details confirmed. Return NO if the booking was incorrect, incomplete, or the wrong action was taken."

### sales
- **Name**: Sales Accuracy
- **Description**: Did the agent provide only accurate information about the product without overselling?
- **Prompt**: "Given the transcript, did the agent provide only accurate information about the product or service without overselling features that do not exist? Return YES if all claims made by the agent are factual and no non-existent features were promised. Return NO if the agent made false claims, exaggerated capabilities, or promised features that don't exist."

### insurance_claims
- **Name**: Identity Verification
- **Description**: Did the agent verify the caller's identity before sharing any account or claim details?
- **Prompt**: "Given the transcript, did the agent verify the caller's identity before sharing any account or claim details? Return YES if the agent requested and confirmed identifying information (policy number, name, DOB, etc.) before disclosing sensitive information. Return NO if the agent shared claim or account details without first verifying the caller's identity."

### healthcare_intake
- **Name**: HIPAA Compliance
- **Description**: Did the agent follow HIPAA guidelines by not sharing medical information without proper verification?
- **Prompt**: "Given the transcript, did the agent follow HIPAA guidelines by not sharing medical information without proper verification? Return YES if the agent verified identity before sharing any medical details and did not disclose protected health information inappropriately. Return NO if the agent shared medical information without verification or violated HIPAA guidelines."

### restaurant_orders
- **Name**: Order Accuracy
- **Description**: Did the agent accurately capture the order including all items, modifications, and special instructions?
- **Prompt**: "Given the transcript, did the agent accurately capture the customer's order including all items, quantities, modifications, and special instructions? Return YES if all items, quantities, modifications, and special requests were correctly recorded and confirmed. Return NO if any items were missed, incorrect, or special instructions were ignored."

### debt_collection
- **Name**: Regulatory Compliance
- **Description**: Did the agent comply with FDCPA requirements?
- **Prompt**: "Given the transcript, did the agent comply with FDCPA (Fair Debt Collection Practices Act) requirements? Return YES if the agent identified themselves properly, did not use threats or abusive language, honored cease-communication requests, and followed proper dispute procedures. Return NO if the agent violated any FDCPA requirements."

### it_helpdesk
- **Name**: Ticket Resolution
- **Description**: Did the agent effectively diagnose and resolve or properly escalate the technical issue?
- **Prompt**: "Given the transcript, did the agent effectively diagnose and resolve (or properly escalate) the technical issue? Return YES if the agent systematically diagnosed the problem, provided a working solution, or escalated to the correct team with sufficient context. Return NO if the agent failed to diagnose, provided incorrect solutions, or left the issue unresolved without escalation."

### other (general fallback)
- **Name**: Task Completion
- **Description**: Did the agent complete the requested task successfully?
- **Prompt**: "Given the transcript, did the agent successfully complete the task requested by the caller? Return YES if the caller's request was fulfilled or appropriately handled. Return NO if the request was not addressed or was handled incorrectly."

## Critical Requirement Metric

If the user provided a critical requirement in Phase 4, create an additional llm-binary metric:

- **Name**: Convert the user's requirement into a **short Title Case noun phrase** following the built-in naming convention (e.g., "Caller Identity Verification", "Feature Claim Accuracy", "Policy Number Collection"). Do NOT use the raw sentence as the name.
- **Description**: The user's full requirement text
- **Prompt**: "Given the transcript, did the agent satisfy this requirement: [CRITICAL REQUIREMENT]? Return YES if the requirement was met. Return NO if the requirement was violated or not addressed."

Replace `[CRITICAL REQUIREMENT]` with the user's exact text.

## Voice-Only Metrics

Only recommend these for `voice` or `outbound-voice` agent types.

### Professional Tone
- **Type**: audio-binary
- **Name**: Professional Tone
- **Description**: Was the agent's tone professional and appropriate throughout the call?
- **Prompt**: "Was the agent's tone professional and appropriate throughout the call?"
- **CLI**: `coval metrics create --name "Professional Tone" --description "Agent tone quality assessment" --type audio-binary --prompt "Was the agent's tone professional and appropriate throughout the call?" --format json`

### Pause Detection
- **Type**: pause
- **Name**: Long Pause Detection
- **Description**: Flags pauses longer than 3 seconds in the conversation
- **CLI**: `coval metrics create --name "Long Pause Detection" --description "Flags pauses longer than 3 seconds" --type pause --min-pause-duration 3.0 --format json`

## CLI Commands

Create an llm-binary metric:
```bash
coval metrics create \
  --name "<name>" \
  --description "<description>" \
  --type llm-binary \
  --prompt "<prompt text>" \
  --format json
```

## Source of Truth

Custom metric names mirror `frontend/features/onboarding/utils/templates.ts` (the `customMetricName` field per vertical). Keep both in sync when updating.
