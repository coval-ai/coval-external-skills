# Persona Templates by Vertical

Select the persona matching the user's use case. Apply their language choice to the description.

## customer_support
- **Name**: Jordan
- **Description**: Customer calling about an issue with their account or service. Expects helpful, efficient support.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: office
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## scheduling_booking
- **Name**: Taylor
- **Description**: Caller looking to book, change, or cancel an appointment. Straightforward, may be in a hurry.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: office
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## sales
- **Name**: Morgan
- **Description**: Potential customer interested in learning about a product or service. Asks questions, may need convincing.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: office
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## insurance_claims
- **Name**: Sarah
- **Description**: Patient, {language}-speaking caller needing help with an insurance claim. Polite, provides info when asked.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: quiet
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## healthcare_intake
- **Name**: Michael
- **Description**: Patient calling to schedule or ask about an appointment. Speaks clearly, may have questions about insurance coverage.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: quiet
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## restaurant_orders
- **Name**: Alex
- **Description**: Hungry customer calling to place or modify a food order. Friendly but wants quick service.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: cafe
- **Wait seconds**: 0.3
- **Conversation initiator**: agent

## debt_collection
- **Name**: Chris
- **Description**: Debtor receiving a collections call. May be defensive, emotional, or disputing the debt.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: quiet
- **Wait seconds**: 1.0
- **Conversation initiator**: persona (outbound — agent calls first)

## it_helpdesk
- **Name**: Pat
- **Description**: Employee calling IT support with a technical issue. May have limited technical knowledge.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: office
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## other (general fallback)
- **Name**: Sam
- **Description**: Standard caller with a straightforward request. Speaks clearly and follows conversational norms.
- **Voice (female)**: aria
- **Voice (male)**: callum
- **Background**: quiet
- **Wait seconds**: 0.5
- **Conversation initiator**: agent

## Language Application

Replace `{language}` in the description with the language name:
- en-US → English
- es-ES → Spanish
- fr-FR → French
- de-DE → German
- pt-BR → Portuguese
- ja-JP → Japanese

Example: "Patient, English-speaking caller needing help with an insurance claim."

## Source of Truth

These templates mirror `frontend/features/onboarding/utils/templates.ts` in the Coval frontend repo. Keep both in sync when updating.
