# NFI Case Management — Delivery Phases

Source: *NFI Application Requirements, External Partner Edition v2* (17 Sep 2026) and the Miro case-stage board.

## Phase 1 — Core case management (Frappe Desk)

Goal: a POC where NFI can run every case end to end inside Frappe. No external integrations. Where the PDF is silent, the POC picks the stricter route and marks it as an assumption so it can be reviewed.

### Masters and roles
- **Hospital Master**: SPOC users (many-to-many), permitted programs (BRP, BCRP, BARP, TBC, SRT), Director per program, NICU beds, MOU expiry date + MOU upload.
- **Program Document Checklist**: per program, intake documents and discharge documents, each Mandatory / Optional / Conditional (e.g. referral letter when Out-born).
- **Roles**: Hospital SPOC, NFI Coordinator, NFI Director, NFI Accountant, NFI Master Admin.
- SPOC sees only cases of mapped hospitals (User Permission on Hospital), including cases created by other SPOCs of the same hospital.

### NFI Case
- Intake fields (Section 5.1): case type (Fresh / Top-up), mother and father name + mobile, generated baby name "B/O <mother>", gender, hospital, program, birth status (In-born / Out-born).
- Documents child table: document type, folder group (Medical / General / Financial / Final), file. Mandatory documents block submission, not Draft.
- Case Number generated on submission. Top-up cases use the `TP` prefix, link to the original case and set a Top-up indicator on it.
- Case-detail fields from Annexure F, entered manually by the Coordinator in this phase.
- Bene Call Notes child table: typed notes, call outcome, repeat calls.
- Money fields stored separately, all manually entered: hospital estimate, recommended support, Director-approved support, final bill, requested top-up, approved top-up, final sponsor amount.
- Lifecycle fields: mortality + date, discharge/death date, final documents received date, payment due date, payment status, post-discharge photo status, video testimonial status, SRT vial count.

### Workflow
- The 13 statuses from Section 16, with an SPOC-facing status that collapses internal stages into "Processing".
- Information needed → SPOC resubmits → Coordinator Verification.
- Program routing after verification:
  - BRP: Medical → Social + Financial in parallel (two review fields, both must be Approved) → amount recommendation → Director.
  - BCRP: Medical → Case Summary → Director.
  - BARP: Director directly.
  - TBC and SRT (POC assumption, route not specified in the PDF): Medical → amount recommendation → Director.
- Committee queries, responses and decisions recorded by the Coordinator in the case (no email capture yet).
- Director Approved / Rejected → Coordinator Review → Approved – Awaiting Final Discharge Documents or Rejected.
- Discharge documents → Accountant Review → Payment Processed / Partially Paid / Paid → Closed.

### Outputs
- Print formats: Case Presentation (Annexure A), BCRP Case Summary (Annexure B).
- Email templates sent from Frappe: hospital approval (Annexure E), SRT approval (Annexure C), rejection (Annexure D). Case Number in the subject.
- Reports replacing the approved-case and rejected-case Excel registers.
- Role dashboards (workspace number cards + charts): SPOC, Coordinator, Director, Accountant, Management.

### SPOC access
- SPOCs use Desk with a restricted role and a single workspace. Custom Desk Pages only where the standard form is not enough.
- Admin screens are plain Desk pages (HTML + CSS + `frappe.ui` components, no Vue build), laid out after the frappe-ui recipes (Tickets for the work queue, Deals for the case pipeline, Accounting for payments).

## Phase 2 — Integrations and portal

- **AI extraction**: Fund Application Form + Interim Summary into case fields (~75% field coverage target), re-trigger after resubmission, unreadable fields flagged.
- **AI call notes**: read a photo of handwritten call notes into the notes field.
- **Email capture**: reviewer emails linked to the case by Case Number in the subject, Unmapped Emails queue with manual linking + audit, per-audience attachment selection.
- **OneDrive**: sync case files to OneDrive in Medical / General / Financial / Final folders; top-ups stored under the original case.
- **SPOC portal**: optional Vue frontend on the same doctypes and APIs, if Desk is not acceptable for hospitals.
- **Bank statement AI evaluation** (future phase per the PDF, Section 7.7).

## POC assumptions (where the PDF is silent)

| # | Gap | POC behaviour |
|---|-----|---------------|
| 1 | TBC / SRT review route | Medical → amount recommendation → Director |
| 2 | Accountant finds a problem | Back to Coordinator Review with a recorded reason |
| 3 | Payment statuses | Accountant records each payment as a row; status becomes Partially Paid while paid < final sponsor amount, Paid when equal; Coordinator sets Closed |
| 4 | "Not specified" checklist cells | Fund Application Form mandatory, every other listed document optional; SRT follows the PDF |
| 5 | SPOC edits on Information needed | Every field except parent names |
| 6 | Top-up eligibility | Any case past Director approval and not Rejected |
| 7 | Mortality during processing | Recorded with date; status is not changed automatically |
| 8 | BARP month-end details | A report filtered to BARP and a month |
| 9 | Committee members | Email-only; the Coordinator records their decisions in the case |
| 10 | No AI in Phase 1 | Submission goes straight from Submitted for Processing to Coordinator Verification; Coordinator types the case fields |

## Open questions for NFI (needed before Phase 1 sign-off)

1. **TBC and SRT review route**: Section 9.5/9.6 says "not specified". The POC routes both through the Medical Committee; confirm or correct.
2. **Document checklist**: most cells are "Not specified" for BRP, BCRP, TBC, BARP; bank and income statement rows are blank for all programs.
3. **Accountant return**: when the Accountant returns a case to the Coordinator, which status does it go to? None exists in Section 16.
4. **Payment statuses**: who sets Payment Processed / Partially Paid / Paid / Closed, and are partial payments recorded as separate entries?
5. **Top-up eligibility**: does "Approved" mean Approved – Awaiting Final Discharge Documents?
6. **SPOC edit scope on return**: which fields count as "unverified" and stay editable for the SPOC?
7. **Mortality**: if the baby dies during processing, does the case status change or continue?
8. **BARP month-end details**: is this a report NFI pulls from the system or a file the hospital uploads?
9. **Committee members**: email-only reviewers, or system users who log in?
10. **Phase 1 without AI**: Coordinator types the Annexure F fields by hand. Confirm NFI accepts this until Phase 2.
