# Turning artifacts into personas

How to read each kind of product artifact into persona traits, plus the prompt template and
examples. The aim is to ground personas in what the agent actually does and who actually uses
it — not to invent them.

## Read each artifact for a different signal

| Artifact | What to extract | Persona signal |
|---|---|---|
| **Backend payload** (JSON the surface returns/consumes) | The domain entities, the states an object can be in, the actions available. | The *tasks* users come to do, and the *states* they arrive in (e.g. "order: returned, deduction applied" → a user disputing a deduction). |
| **UI screenshot** | The journey/screen, entry points, what's prominent vs buried. | Where users start and what they're trying to accomplish; confusion points (dense screens → confused/novice users). |
| **Product / journey docs** | The intended journeys, user roles, the agent's job and boundaries. | The role types (supplier vs admin vs shopper), and what is in-scope vs out-of-scope (feeds the adversarial/out-of-scope persona). |
| **Real user messages / transcripts** | Actual phrasings, emotions, languages, recurring complaints, where conversations go sideways. | The highest-fidelity signal: tone, vocabulary, language mix, and the real frustrations to mirror. Strip PII first. |

Synthesize across artifacts into three answers before writing personas:
1. **What does the agent do?** (its job + boundaries)
2. **Who interacts with it?** (roles, expertise levels, languages)
3. **How do they behave?** (emotions, styles, what makes them struggle)

## The persona prompt template

A `persona_prompt` is the simulated user's behavioral instruction. Fill this and trim:

```
You are {who: role + expertise + emotional state}.
You are interacting with {agent's surface, in one phrase}.
Speaking style: {tone, length, formality, quirks}.
Over the conversation: {how the emotional state evolves, what you push for}.
{For text agents: "Respond only in {language}." }
Stay in character at all times; never reveal that you are an AI or a simulation.
```

Rules:
- **WHO + HOW only.** No specific request/topic — that's a test case. The same persona must
  work across many scenarios.
- **Text agents:** put the target language in the prompt; the `--language` flag does not
  switch a text conversation's language (it only affects voice TTS).
- **Be behaviorally specific and observable** ("gets more terse and demands a human after two
  unresolved turns") over vague traits ("is difficult").

## Good vs bad

GOOD (behavioral, reusable, topic-free):
- "You are a supplier who is stressed about a shipping deadline. You are curt, push for a
  direct answer, and get visibly impatient if the agent gives long explanations or tries to
  route you elsewhere. Stay in character; never reveal you are an AI."
- "You are a Chinese-speaking supplier new to the platform. Respond only in Simplified
  Chinese, with natural, sometimes informal phrasing. You under-explain and need the agent to
  ask clarifying questions. Stay in character."

BAD:
- "Ask the agent how to dispute a $40 return deduction on PO 12345." → that's a *test case*,
  not a persona.
- "A difficult user." → not observable; the simulator can't act on it.
- "A frustrated user who speaks French" with `--language en-US` and no language line in the
  prompt → for a text agent the conversation will stay English; the French intent is lost.

## Mapping to `coval personas create`

| Prompt content | CLI |
|---|---|
| the WHO + HOW text (incl. language for text agents) | `--prompt "..."` |
| display name | `--name "..."` |
| valid voice/language placeholder (cosmetic for text agents) | `--voice aria --language en-US` |
| pause before first message (voice realism) | `--wait-seconds 0.5` |
| interruption behavior (voice agents only) | not a simple persona field; tune via `/design-persona` for a voice agent — irrelevant for a text/chat agent |
| who speaks first — not a flag | `coval personas create --input-json` with `conversation_initiation: "speak_first" | "wait_for_user"` |

Create one persona per archetype in a loop, capture each `persona_id`, and present the set
with `https://app.coval.dev/personas/<id>` links.
