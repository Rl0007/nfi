# NFI backend (Phase 1 POC)

Module "NFI". Roles: NFI SPOC, NFI Coordinator, NFI Director, NFI Accountant, NFI Admin.
Programs, roles and the workflow are created by `nfi/install.py` (after_install; roles + workflow also after_migrate).

## DocTypes
- **NFI Program** (name = code BRP/BCRP/BARP/TBC/SRT): review_route ("Medical, Social & Financial" / "Medical" / "Director Only"), fixed_amount, documents → NFI Program Document (document_type, stage Intake/Discharge, requirement, folder).
- **NFI Hospital** (name = hospital_name): city, nicu_beds, mou_expiry_date, mou_file, spocs → NFI Hospital SPOC (user), programs → NFI Hospital Program (program, director).
- **NFI Case** (hash name, title = baby_name, user-facing `case_number` NFI-YYYY-##### / TP-YYYY-#####). Tabs: Intake, Fund Application (`fa_*`), Interim Summary (`interim_*`), Verification, Review, Money, Outcome & Payment, Lifecycle.
  - Children: documents → NFI Case Document, bene calls → NFI Bene Call, review_log → NFI Review Log, payments → NFI Payment.
  - Review: medical_status, social_status, financial_status; director, director_decision.
  - Money: hospital_estimate, recommended_amount, director_approved_amount, final_bill, requested_topup, approved_topup, final_sponsor_amount, srt_vials, total_paid.
  - spoc_status: internal stages shown as "Processing".
- Field levels: case details / review / money / payments / lifecycle are permlevel 1 (SPOC can't read). rejection_reason, return_reason permlevel 2 (SPOC read-only).

## Workflow "NFI Case Workflow"
Draft →Submit→ Coordinator Verification (Submitted for Processing passed through) →
- Request Information → Information needed →Resubmit→ Coordinator Verification
- Send to Medical Review → Medical Review → (full route) Send to Social & Financial Review → Social & Financial Review → Send to Director
- (Medical route: BCRP/TBC/SRT) Medical Review → Send to Director (needs recommended_amount)
- (Director Only: BARP) Send to Director
- Reject (needs rejection_reason) → Rejected
Director Review →Approve/Reject (Director)→ Coordinator Review →Approve→ Approved – Awaiting Final Discharge Documents →Send to Accountant→ Accountant Review →Process Payment (Accountant)→ Payment Processed → Partially Paid / Paid (auto from payments) →Close→ Closed. Accountant can Return to Coordinator (return_reason).
Director Approved / Director Rejected / Submitted for Processing are never persisted (pass-through via db_set in on_update).

## Permissions
`nfi/permissions.py` via hooks: SPOC sees cases of hospitals where they are a SPOC; Director sees cases where director = user; Coordinator/Accountant/Admin see all. Server-side SPOC edit locks in nfi_case.py.
