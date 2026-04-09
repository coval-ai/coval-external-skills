# Agent Connection Types

Reference for agent type selection and configuration. Each type defines how Coval connects to the agent under test.

## voice (MODEL_TYPE_VOICE)

Inbound phone calls — Coval calls the agent's phone number and the agent speaks first.

- **Required fields**: `phone_number`
- **Optional fields**: `prompt`, `language`, `metadata`
- **Validation**: Phone number must be E.164 format (`+` followed by 10-15 digits, e.g. `+12345678901`)
- **How it works**: Coval's persona dials the number, the agent picks up and speaks first, then the persona responds according to the test case scenario.
- **Common pitfalls**:
  - Forgetting the `+` prefix or country code
  - Using formatting characters (spaces, dashes, parentheses) — strip these
  - Agent not configured to accept calls from unknown numbers
  - Agent has an IVR menu before reaching the AI — ensure direct routing

## outbound-voice (MODEL_TYPE_OUTBOUND_VOICE)

Agent calls out — Coval triggers the agent to initiate an outbound call, and the persona answers.

- **Required fields**: `endpoint` (URL that triggers the agent to call)
- **Optional fields**: `prompt`, `language`, `metadata`
- **Validation**: Must be a valid HTTP or HTTPS URL
- **How it works**: Coval sends a request to the endpoint to trigger the agent to call a Coval-provisioned number. The persona picks up and responds according to the test case.
- **Common pitfalls**:
  - Endpoint must accept POST requests with a JSON body containing the target phone number
  - Agent may have rate limits on outbound calls
  - Ensure the endpoint is publicly accessible (not behind a VPN or firewall)

## chat (MODEL_TYPE_CHAT)

Text/API endpoint — Coval sends messages to the agent's HTTP endpoint in OpenAI-compatible format.

- **Required fields**: `endpoint` (URL)
- **Optional fields**: `prompt`, `metadata`
- **Validation**: Must be a valid HTTP or HTTPS URL
- **How it works**: Coval sends chat completion requests to the endpoint. The agent responds with text. Supports multi-turn conversations.
- **Expected format**: OpenAI-compatible chat completions API (`/v1/chat/completions` style)
- **Common pitfalls**:
  - Endpoint must accept POST requests with `messages` array in OpenAI format
  - Ensure the endpoint handles conversation history (multi-turn)
  - CORS or authentication issues if the endpoint requires API keys — configure in agent metadata
  - Timeout settings — ensure the endpoint responds within 30 seconds

## sms (SMS)

SMS-based agent — Coval sends text messages to the agent's phone number.

- **Required fields**: `phone_number`
- **Optional fields**: `prompt`, `metadata`
- **Validation**: Phone number must be E.164 format (`+` followed by 10-15 digits, e.g. `+12345678901`)
- **How it works**: Coval sends SMS messages to the phone number. The agent responds via SMS. Supports multi-turn text conversations.
- **Common pitfalls**:
  - Same E.164 validation as voice
  - Agent must be configured to respond to SMS from unknown numbers
  - SMS rate limits may apply
  - Message length limits (160 chars per segment) — long agent responses may be split

## websocket (MODEL_TYPE_WEBSOCKET)

WebSocket connection — Coval connects to the agent via WebSocket for real-time bidirectional communication.

- **Required fields**: `endpoint` (WebSocket URL)
- **Optional fields**: `prompt`, `metadata`
- **Validation**: Must be a valid WebSocket URL (`ws://` or `wss://`)
- **How it works**: Coval opens a WebSocket connection to the endpoint and exchanges messages in real-time. Supports streaming responses.
- **Common pitfalls**:
  - Use `wss://` for production (encrypted) — `ws://` is only for local development
  - Ensure the WebSocket server handles connection lifecycle (open, message, close, error)
  - Authentication may need to be passed as query parameters or in the initial handshake
  - Keep-alive / ping-pong settings — ensure the connection doesn't timeout during long conversations

## api (MODEL_TYPE_API)

Generic API endpoint — Coval sends requests to a custom API endpoint.

- **Required fields**: `endpoint` (URL)
- **Optional fields**: `prompt`, `metadata`
- **Validation**: Must be a valid HTTP or HTTPS URL
- **How it works**: Coval sends requests to the endpoint following the agent's custom API format. Use this when the agent doesn't follow OpenAI-compatible format.
- **Common pitfalls**:
  - Ensure the API format is documented in agent metadata
  - Authentication headers may be required
  - Response format must be parseable by Coval

## endpoint (MODEL_TYPE_ENDPOINT)

Custom endpoint — Coval connects to a custom endpoint with flexible configuration.

- **Required fields**: `endpoint` (URL)
- **Optional fields**: `prompt`, `metadata`
- **Validation**: Must be a valid HTTP or HTTPS URL
- **How it works**: Similar to API type but with more flexible configuration options. Use for agents with non-standard connection requirements.
- **Common pitfalls**:
  - Same as API type
  - Ensure custom configuration is properly documented in metadata

## Quick Reference

| Type | Connection | Required Field | Who Speaks First |
|------|-----------|----------------|-----------------|
| voice | Phone call (inbound) | `phone_number` (E.164) | Agent |
| outbound-voice | Phone call (outbound) | `endpoint` (URL) | Persona |
| chat | HTTP API | `endpoint` (URL) | Persona |
| sms | SMS | `phone_number` (E.164) | Persona |
| websocket | WebSocket | `endpoint` (ws/wss URL) | Persona |
| api | HTTP API | `endpoint` (URL) | Persona |
| endpoint | HTTP API | `endpoint` (URL) | Persona |
