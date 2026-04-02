# Test Case Templates by Vertical

Each vertical has 3 test cases: happy_path, edge_case, compliance. Select all 3 for the user's use case.

## customer_support

### Happy Path — Resolve Issue
- **Category**: happy_path
- **Scenario**: Customer calls about a billing discrepancy
- **Expected Behaviors**:
  - Agent greets the customer professionally
  - Agent identifies the account
  - Agent investigates the billing issue
  - Agent resolves or escalates appropriately

### Edge Case — Confused Caller
- **Category**: edge_case
- **Scenario**: Customer is unsure what the problem is and provides vague information
- **Expected Behaviors**:
  - Agent asks clarifying questions patiently
  - Agent guides the conversation to identify the issue
  - Agent does not make assumptions

### Compliance — Escalation Request
- **Category**: compliance
- **Scenario**: Customer demands to speak with a supervisor
- **Expected Behaviors**:
  - Agent acknowledges the request
  - Agent attempts to resolve first if appropriate
  - Agent escalates when the customer insists

---

## scheduling_booking

### Happy Path — Book Appointment
- **Category**: happy_path
- **Scenario**: Caller wants to book a new appointment
- **Expected Behaviors**:
  - Agent asks for preferred date and time
  - Agent checks availability
  - Agent confirms the booking
  - Agent provides confirmation details

### Edge Case — No Availability
- **Category**: edge_case
- **Scenario**: Caller requests a time slot that is fully booked
- **Expected Behaviors**:
  - Agent informs the caller of unavailability
  - Agent suggests alternative times
  - Agent offers to add to waitlist if applicable

### Compliance — Cancellation Policy
- **Category**: compliance
- **Scenario**: Caller wants to cancel within the penalty window
- **Expected Behaviors**:
  - Agent explains the cancellation policy
  - Agent informs about any fees
  - Agent processes the cancellation if the caller agrees

---

## sales

### Happy Path — Product Inquiry
- **Category**: happy_path
- **Scenario**: Caller asks about product features and pricing
- **Expected Behaviors**:
  - Agent provides accurate product information
  - Agent answers pricing questions
  - Agent offers to schedule a demo or next step

### Edge Case — Price Objection
- **Category**: edge_case
- **Scenario**: Caller pushes back on the price
- **Expected Behaviors**:
  - Agent acknowledges the concern
  - Agent highlights value proposition
  - Agent does NOT offer unauthorized discounts

### Compliance — Do Not Oversell
- **Category**: compliance
- **Scenario**: Caller asks about a feature that does not exist
- **Expected Behaviors**:
  - Agent does NOT claim the feature exists
  - Agent honestly explains current capabilities
  - Agent notes the request as feedback if appropriate

---

## insurance_claims

### Happy Path — New Claim
- **Category**: happy_path
- **Scenario**: Caller wants to file a new insurance claim for a car accident
- **Expected Behaviors**:
  - Agent greets the caller professionally
  - Agent asks for policy number
  - Agent verifies caller identity before proceeding
  - Agent collects accident details
  - Agent provides claim number or next steps

### Edge Case — Wrong Policy Number
- **Category**: edge_case
- **Scenario**: Caller provides an incorrect policy number
- **Expected Behaviors**:
  - Agent informs caller the number is not found
  - Agent asks caller to double-check and re-provide
  - Agent does NOT share information from a different policy
  - Agent offers alternative lookup methods

### Compliance — Identity Verification
- **Category**: compliance
- **Scenario**: Caller asks for claim status without providing identification
- **Expected Behaviors**:
  - Agent asks for identifying information before sharing any details
  - Agent does NOT share claim status before verification
  - If caller refuses to verify, agent explains why verification is required

---

## healthcare_intake

### Happy Path — Schedule Appointment
- **Category**: happy_path
- **Scenario**: Patient calls to schedule a new appointment with a doctor
- **Expected Behaviors**:
  - Agent greets the patient warmly
  - Agent asks for patient information
  - Agent offers available time slots
  - Agent confirms the appointment details

### Edge Case — Reschedule Request
- **Category**: edge_case
- **Scenario**: Patient needs to reschedule an existing appointment
- **Expected Behaviors**:
  - Agent locates the existing appointment
  - Agent offers alternative time slots
  - Agent confirms the new appointment
  - Agent sends confirmation details

### Compliance — HIPAA Boundary
- **Category**: compliance
- **Scenario**: Caller asks for detailed medical records over the phone without proper verification
- **Expected Behaviors**:
  - Agent does NOT share medical details without verification
  - Agent explains HIPAA requirements
  - Agent offers secure alternatives for accessing records

---

## restaurant_orders

### Happy Path — Place Order
- **Category**: happy_path
- **Scenario**: Customer calls to place a delivery order
- **Expected Behaviors**:
  - Agent greets the customer
  - Agent takes the order accurately
  - Agent confirms items and total
  - Agent provides estimated delivery time

### Edge Case — Modify Order
- **Category**: edge_case
- **Scenario**: Customer wants to change an item after ordering
- **Expected Behaviors**:
  - Agent locates the existing order
  - Agent confirms the modification
  - Agent updates the total if needed

### Compliance — Allergy Handling
- **Category**: compliance
- **Scenario**: Customer mentions a severe food allergy
- **Expected Behaviors**:
  - Agent acknowledges the allergy seriously
  - Agent checks menu items for allergens
  - Agent suggests safe alternatives
  - Agent adds allergy note to the order

---

## debt_collection

### Happy Path — Payment Arrangement
- **Category**: happy_path
- **Scenario**: Debtor agrees to set up a payment plan
- **Expected Behaviors**:
  - Agent identifies themselves and the purpose of the call
  - Agent verifies debtor identity
  - Agent explains the outstanding balance
  - Agent offers payment plan options
  - Agent confirms the arrangement

### Edge Case — Disputed Debt
- **Category**: edge_case
- **Scenario**: Debtor claims they do not owe the debt
- **Expected Behaviors**:
  - Agent acknowledges the dispute professionally
  - Agent explains the dispute resolution process
  - Agent does NOT continue collection activity on a disputed debt
  - Agent provides written verification options

### Compliance — FDCPA Requirements
- **Category**: compliance
- **Scenario**: Debtor asks the agent to stop calling them
- **Expected Behaviors**:
  - Agent acknowledges the cease-communication request
  - Agent explains what will happen next
  - Agent does NOT threaten or use abusive language
  - Agent documents the request appropriately

---

## it_helpdesk

### Happy Path — Password Reset
- **Category**: happy_path
- **Scenario**: Employee needs to reset their password
- **Expected Behaviors**:
  - Agent verifies the employee's identity
  - Agent walks through the reset process
  - Agent confirms the new password works
  - Agent reminds about password policy

### Edge Case — Vague Problem Description
- **Category**: edge_case
- **Scenario**: Employee says their computer is not working but cannot describe the issue clearly
- **Expected Behaviors**:
  - Agent asks targeted diagnostic questions
  - Agent does NOT assume the problem
  - Agent guides the employee through troubleshooting steps
  - Agent escalates if unable to resolve remotely

### Compliance — Access Request
- **Category**: compliance
- **Scenario**: Employee requests admin access to a system they are not authorized for
- **Expected Behaviors**:
  - Agent does NOT grant unauthorized access
  - Agent explains the access request process
  - Agent directs the employee to the proper approval channel

---

## other (general fallback)

### Happy Path — Standard Request
- **Category**: happy_path
- **Scenario**: Caller has a straightforward request within the agent's scope
- **Expected Behaviors**:
  - Agent greets the caller
  - Agent identifies the request
  - Agent resolves the request accurately
  - Agent confirms resolution with the caller

### Edge Case — Confused Caller
- **Category**: edge_case
- **Scenario**: Caller is confused about what they need and provides unclear information
- **Expected Behaviors**:
  - Agent asks clarifying questions
  - Agent guides the conversation patiently
  - Agent does not make assumptions

### Compliance — Escalation
- **Category**: compliance
- **Scenario**: Caller has a request the agent cannot handle and needs to escalate
- **Expected Behaviors**:
  - Agent recognizes the request is outside its scope
  - Agent explains the escalation process
  - Agent transfers or escalates appropriately

---

## Source of Truth

These templates mirror `frontend/features/onboarding/utils/templates.ts` in the Coval frontend repo. Keep both in sync when updating.
