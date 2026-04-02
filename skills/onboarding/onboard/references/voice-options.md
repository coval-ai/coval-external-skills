# Voice Options Reference

## Available Voices

Use `coval personas phone-numbers` to list available phone numbers.

### Default Voices
| Voice Name | Gender | Best For |
|------------|--------|----------|
| aria | Female | Standard, clear, professional |
| callum | Male | Standard, clear, professional |

### Language Codes (BCP-47)
| Code | Language | Display Name |
|------|----------|-------------|
| en-US | English (US) | English |
| es-ES | Spanish (Spain) | Spanish |
| fr-FR | French (France) | French |
| de-DE | German | German |
| pt-BR | Portuguese (Brazil) | Portuguese |
| ja-JP | Japanese | Japanese |

## Background Sounds
| Value | Description | Use For |
|-------|-------------|---------|
| quiet | No background noise | Medical, legal, financial calls |
| office | Office ambient noise | Corporate/business calls |
| cafe | Restaurant/cafe noise | Casual/restaurant scenarios |
| airport | Airport/travel noise | Travel-related agents |

## Wait Seconds
How long the persona waits before speaking after the call connects.
- **0.3** — Quick response (restaurant orders, fast-paced)
- **0.5** — Standard (most inbound calls)
- **1.0** — Slower (outbound calls where agent speaks first, debt collection)

## Conversation Initiator
- **agent** — Agent speaks first (standard for inbound calls)
- **persona** — Persona speaks first (outbound calls where the agent initiates)
