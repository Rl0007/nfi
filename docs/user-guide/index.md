# NFI user guide: index and writer's brief

Writer and reviewer agents read this before they touch a page.

Status: **draft, awaiting approval.**

## Decisions

| Question | Decision |
|---|---|
| Audience | The five people who use NFI daily: hospital SPOC, NFI coordinator, director, accountant, NFI admin. Non-technical. |
| Structure | One part per role, in the order a case moves (SPOC → Coordinator → Director → Accountant), plus a short "how a case moves" overview and an admin part. A reader only needs their own part. |
| Surface | Desk as each role sees it: their workspace, the NFI Case form, Case Desk, Payments, reports. Exact on-screen labels. |
| Screenshots | Live from nfi.localhost with the demo data, logged in as the role. Cropped to the area that matters, red box on the button/field the step talks about (pr-screenshots style). Light theme. |
| Phase 2 items | AI reading, OneDrive, email-reply capture: one "Coming later" note on the overview page only. |
| Publish target | agrawalrahul.in, wiki space `nfi` (frappectl profile "Me prod"), via the app-setup-docs publisher. |
| Voice | "case", "hospital", "approve" — never DocType, workflow state, permlevel. Steps are numbered clicks. Each page ends with "How you know it worked". |

## Section index

```
01  how-nfi-works  How a case moves through NFI
  COVERS:   the whole journey in one picture; who does what; the statuses a hospital sees vs NFI sees
  SURFACE:  NFI Case statuses; programs BRP, BCRP, BARP, TBC, SRT and their review routes
  RESULT:   reader knows which part of the guide is theirs
  SHOTS:    Case Desk pipeline (overview); one Mermaid flow per review route
  DEPENDS:  —

02  sign-in  Sign in and find your home screen
  COVERS:   log in, land on your role's workspace, read the number cards
  SURFACE:  /login; workspaces NFI SPOC / NFI Coordinator / NFI Director / NFI Accountant / NFI Management
  RESULT:   you see your own cards and only your cases
  SHOTS:    login page; each role's workspace (small)
  DEPENDS:  —

--- Hospital SPOC ---
03  spoc-new-case  Submit a new case
  COVERS:   Fresh Case: hospital, program, parents, birth status; baby name fills itself; upload documents; save draft; submit
  SURFACE:  NFI Case form Intake tab; documents table (mandatory rows); Actions → Submit; case number appears
  RESULT:   status Coordinator Verification and an NFI-YYYY-#### case number
  SHOTS:    new form; documents table; blocked-submit message; submitted case with number
  DEPENDS:  02

04  spoc-information-needed  Fix a case NFI sent back
  COVERS:   find returned cases, read the reason, correct, resubmit; parent names locked
  SURFACE:  "Information needed" card; Return Reason; Actions → Resubmit
  RESULT:   status back to Coordinator Verification
  SHOTS:    card; reason on form; resubmit action
  DEPENDS:  03

05  spoc-discharge  Send discharge documents after approval
  COVERS:   approval email, upload final documents, what NFI needs per program (general vs SRT)
  SURFACE:  "Awaiting discharge docs" card; Discharge rows in documents table
  RESULT:   NFI coordinator can send it to the accountant
  SHOTS:    card; discharge rows uploaded
  DEPENDS:  03

06  spoc-top-up  Ask for more money (top-up)
  COVERS:   Top-up case type, pick the original case, choose program, TP number
  SURFACE:  Case Type = Top-up; Original Case
  RESULT:   new TP-YYYY-#### case linked to the original
  SHOTS:    case type + original case picker; TP number
  DEPENDS:  03

--- NFI Coordinator ---
07  coordinator-case-desk  Your work queue: Case Desk
  COVERS:   My Queue and Pipeline, filters, opening a case
  SURFACE:  /desk/nfi-case-desk
  RESULT:   you know what needs you next
  SHOTS:    My Queue; Pipeline; filters
  DEPENDS:  02

08  coordinator-verify  Verify a case and call the family
  COVERS:   check intake + documents, fill case details, log the beneficiary call, send back / reject / move on
  SURFACE:  Fund Application + Interim Summary tabs; Verification tab (bene calls); Actions → Request Information / Reject / Send to …
  RESULT:   case in the right review step for its program
  SHOTS:    case details tab; bene call row; Actions menu
  DEPENDS:  07

09  coordinator-reviews  Run the committee reviews
  COVERS:   Medical, then Social & Financial (BRP); record queries, answers, decisions; recommend an amount; send to Director
  SURFACE:  Review tab statuses; Review Log; Recommended Amount; Actions → Send to Director
  RESULT:   case in Director Review
  SHOTS:    review statuses; review log; send to director
  DEPENDS:  08

10  coordinator-decision  Tell the hospital: approve or reject
  COVERS:   after the director decides, approve (email goes to hospital) or reject with reason
  SURFACE:  Coordinator Review; Director Decision; Actions → Approve / Reject; Rejection Reason
  RESULT:   Approved – Awaiting Final Discharge Documents or Rejected; email queued
  SHOTS:    director decision field; actions; approval email preview
  DEPENDS:  09

11  coordinator-close  Send to accountant and close the case
  COVERS:   check discharge documents, send to accountant, handle a returned case, close after payment
  SURFACE:  Actions → Send to Accountant / Close
  RESULT:   Closed
  SHOTS:    send to accountant; closed case
  DEPENDS:  10

12  coordinator-print  Print the case presentation and summary
  COVERS:   Case Presentation (all programs) and BCRP Case Summary
  SURFACE:  Print → NFI Case Presentation / NFI BCRP Case Summary → PDF
  RESULT:   PDF to share with the committee
  SHOTS:    print preview of each
  DEPENDS:  08

--- Director ---
13  director-decide  Approve or reject a case
  COVERS:   your workspace, open a case awaiting you, read the presentation, approve or reject
  SURFACE:  NFI Director workspace; Actions → Approve / Reject
  RESULT:   case goes back to the coordinator
  SHOTS:    awaiting card; case; actions
  DEPENDS:  02

--- Accountant ---
14  accountant-pay  Check documents and record payments
  COVERS:   Payments page, open a case, return to coordinator if something is missing, Process Payment, add payments (partial / full)
  SURFACE:  /desk/nfi-payments; Payments table; Actions → Process Payment / Return to Coordinator
  RESULT:   Partially Paid → Paid
  SHOTS:    payments page; payments table; status after payment
  DEPENDS:  02

--- Reports ---
15  reports  Registers and reports
  COVERS:   Approved / Rejected registers, BARP Monthly, Payments Due; filters; export
  SURFACE:  the four reports
  RESULT:   the list you used to keep in Excel
  SHOTS:    each report with filters
  DEPENDS:  02

--- NFI Admin ---
16  admin-hospitals  Add a hospital and its SPOCs
  COVERS:   hospital details, MOU, SPOC users, programs and their director
  SURFACE:  NFI Hospital form; SPOCs table; Programs table
  RESULT:   the SPOC can sign in and submit cases for that hospital
  SHOTS:    hospital form; tables
  DEPENDS:  —

17  admin-programs  Programs and document checklists
  COVERS:   review route, fixed amount, intake/discharge checklist per program
  SURFACE:  NFI Program form; Documents table
  RESULT:   new cases show the right document rows
  SHOTS:    program form; checklist
  DEPENDS:  —
```

OUT-OF-SCOPE: AI document reading, OneDrive, email-reply capture, bank-statement evaluation (Phase 2); System Manager / Desk setup screens; developer setup.
