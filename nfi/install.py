import frappe

SPOC = "NFI SPOC"
COORDINATOR = "NFI Coordinator"
DIRECTOR = "NFI Director"
ACCOUNTANT = "NFI Accountant"
ADMIN = "NFI Admin"
ROLES = (SPOC, COORDINATOR, DIRECTOR, ACCOUNTANT, ADMIN)

APPROVED_AWAITING_DOCUMENTS = "Approved – Awaiting Final Discharge Documents"  # noqa: RUF001
WORKFLOW_NAME = "NFI Case Workflow"

STATE_EDITORS = {
	"Draft": [SPOC, COORDINATOR],
	"Submitted for Processing": [COORDINATOR],
	"Information needed": [SPOC],
	"Coordinator Verification": [COORDINATOR],
	"Medical Review": [COORDINATOR],
	"Social & Financial Review": [COORDINATOR],
	"Director Review": [DIRECTOR, COORDINATOR],
	"Director Approved": [COORDINATOR],
	"Director Rejected": [COORDINATOR],
	"Coordinator Review": [COORDINATOR],
	APPROVED_AWAITING_DOCUMENTS: [COORDINATOR, SPOC],
	"Accountant Review": [ACCOUNTANT, COORDINATOR],
	"Rejected": [ADMIN],
	"Payment Processed": [ACCOUNTANT],
	"Partially Paid": [ACCOUNTANT],
	"Paid": [COORDINATOR, ACCOUNTANT],
	"Closed": [ADMIN],
}
STATE_STYLES = {
	"Draft": "",
	"Information needed": "Warning",
	"Director Approved": "Success",
	"Director Rejected": "Danger",
	APPROVED_AWAITING_DOCUMENTS: "Success",
	"Rejected": "Danger",
	"Partially Paid": "Warning",
	"Paid": "Success",
	"Closed": "Inverse",
}
STATE_UPDATES = {
	"Director Approved": ("director_decision", "Approved"),
	"Director Rejected": ("director_decision", "Rejected"),
}

FULL_ROUTE = "Medical, Social & Financial"
TRANSITIONS = [
	("Draft", "Submit", "Submitted for Processing", SPOC, None),
	("Draft", "Submit", "Submitted for Processing", COORDINATOR, None),
	("Information needed", "Resubmit", "Coordinator Verification", SPOC, None),
	("Coordinator Verification", "Request Information", "Information needed", COORDINATOR, None),
	(
		"Coordinator Verification",
		"Send to Medical Review",
		"Medical Review",
		COORDINATOR,
		f"doc.review_route in ('{FULL_ROUTE}', 'Medical')",
	),
	(
		"Coordinator Verification",
		"Send to Director",
		"Director Review",
		COORDINATOR,
		"doc.review_route == 'Director Only'",
	),
	("Coordinator Verification", "Reject", "Rejected", COORDINATOR, None),
	(
		"Medical Review",
		"Send to Social & Financial Review",
		"Social & Financial Review",
		COORDINATOR,
		f"doc.review_route == '{FULL_ROUTE}' and doc.medical_status == 'Approved'",
	),
	(
		"Medical Review",
		"Send to Director",
		"Director Review",
		COORDINATOR,
		"doc.review_route == 'Medical' and doc.medical_status == 'Approved' and doc.recommended_amount",
	),
	(
		"Medical Review",
		"Send to Coordinator Review",
		"Coordinator Review",
		COORDINATOR,
		"doc.medical_status == 'Rejected'",
	),
	(
		"Social & Financial Review",
		"Send to Director",
		"Director Review",
		COORDINATOR,
		"doc.social_status == 'Approved' and doc.financial_status == 'Approved' and doc.recommended_amount",
	),
	(
		"Social & Financial Review",
		"Send to Coordinator Review",
		"Coordinator Review",
		COORDINATOR,
		"'Rejected' in (doc.social_status, doc.financial_status)",
	),
	("Director Review", "Approve", "Director Approved", DIRECTOR, None),
	("Director Review", "Reject", "Director Rejected", DIRECTOR, None),
	(
		"Coordinator Review",
		"Approve",
		APPROVED_AWAITING_DOCUMENTS,
		COORDINATOR,
		"doc.director_decision == 'Approved'",
	),
	("Coordinator Review", "Reject", "Rejected", COORDINATOR, None),
	(
		"Coordinator Review",
		"Send to Accountant",
		"Accountant Review",
		COORDINATOR,
		"doc.director_decision == 'Approved' and doc.final_documents_received_date",
	),
	(APPROVED_AWAITING_DOCUMENTS, "Send to Accountant", "Accountant Review", COORDINATOR, None),
	("Accountant Review", "Process Payment", "Payment Processed", ACCOUNTANT, None),
	("Accountant Review", "Return to Coordinator", "Coordinator Review", ACCOUNTANT, None),
	("Paid", "Close", "Closed", COORDINATOR, None),
]

FUND_APPLICATION_FORM = "Fund Application Form"
INTERIM_SUMMARY = "Interim Summary"
FATHER_AADHAAR = "Father Aadhaar Card"
MOTHER_AADHAAR = "Mother Aadhaar Card"
BOTH_PARENTS_AADHAAR = "Both Parents Aadhaar Card"

GENERAL_INTAKE_DOCUMENTS = [
	(FUND_APPLICATION_FORM, "General"),
	(INTERIM_SUMMARY, "Medical"),
	(FATHER_AADHAAR, "General"),
	(MOTHER_AADHAAR, "General"),
	(BOTH_PARENTS_AADHAAR, "General"),
	("BPL Card or Ration Card", "Financial"),
	("Referral Letter from Birth Hospital", "Medical"),
	("Baby NICU Photo with ID Band", "Medical"),
	("Bank Statement (6 Months)", "Financial"),
	("Income Statement", "Financial"),
	("Other Documents", "General"),
]
SRT_INTAKE_REQUIREMENTS = {
	FUND_APPLICATION_FORM: "Mandatory",
	INTERIM_SUMMARY: "Mandatory",
	FATHER_AADHAAR: "Mandatory",
	MOTHER_AADHAAR: "Mandatory",
	"BPL Card or Ration Card": "Mandatory",
	"Referral Letter from Birth Hospital": "Mandatory when Out-born",
	"Baby NICU Photo with ID Band": "Mandatory",
	"Video of Surfactant Administration": "Mandatory",
}
GENERAL_DISCHARGE_DOCUMENTS = [
	("Final Discharge Summary", "Mandatory"),
	("Final Bills with Hospital Discount and NFI Sponsor Fund", "Mandatory"),
	("Additional Treatment Bills or Receipts", "Optional"),
	("Informed Consent for Post-discharge Video and Pictures", "Mandatory"),
	("Payment Requisition Letter", "Mandatory"),
]
SRT_DISCHARGE_DOCUMENTS = [
	("Final Discharge Summary with Vial Sticker", "Mandatory"),
	("Final Bill with Surfactant Bill", "Mandatory"),
	("Final Bills Mentioning NFI Sponsor Fund", "Mandatory"),
	("Payment Requisition Letter", "Mandatory"),
]
PROGRAMS = [
	("BRP", "Beneficiary Review Committee", FULL_ROUTE, 0, {INTERIM_SUMMARY: "Mandatory"}),
	("BCRP", "Beneficiary Clinical Review Process", "Medical", 0, {}),
	("BARP", "Beneficiary Aid Recommendation Panel", "Director Only", 0, {}),
	("TBC", "Total Body Cooling", "Medical", 50000, {}),
	("SRT", "Surfactant Replacement Therapy", "Medical", 0, SRT_INTAKE_REQUIREMENTS),
]


def after_install():
	add_roles()
	add_workflow()
	add_programs()


def after_migrate():
	add_roles()
	add_workflow()


def add_roles():
	for role_name in ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert()


def add_workflow():
	for state in STATE_EDITORS:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc(
				{
					"doctype": "Workflow State",
					"workflow_state_name": state,
					"style": STATE_STYLES.get(state, ""),
				}
			).insert()
	for action in {transition[1] for transition in TRANSITIONS}:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert()

	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		workflow = frappe.get_doc("Workflow", WORKFLOW_NAME)
	else:
		workflow = frappe.new_doc("Workflow")
		workflow.workflow_name = WORKFLOW_NAME
	workflow.update(
		{
			"document_type": "NFI Case",
			"workflow_state_field": "workflow_state",
			"is_active": 1,
			"send_email_alert": 0,
			"states": [],
			"transitions": [],
		}
	)
	for state, editors in STATE_EDITORS.items():
		update_field, update_value = STATE_UPDATES.get(state, (None, None))
		for role in editors:
			workflow.append(
				"states",
				{
					"state": state,
					"doc_status": "0",
					"allow_edit": role,
					"update_field": update_field,
					"update_value": update_value,
				},
			)
	for state, action, next_state, role, condition in TRANSITIONS:
		workflow.append(
			"transitions",
			{
				"state": state,
				"action": action,
				"next_state": next_state,
				"allowed": role,
				"condition": condition,
				"allow_self_approval": 1,
			},
		)
	workflow.save()


def add_programs():
	for code, program_name, review_route, fixed_amount, intake_requirements in PROGRAMS:
		if frappe.db.exists("NFI Program", code):
			continue
		program = frappe.new_doc("NFI Program")
		program.update(
			{
				"__newname": code,
				"program_name": program_name,
				"review_route": review_route,
				"fixed_amount": fixed_amount,
			}
		)
		intake_documents = list(GENERAL_INTAKE_DOCUMENTS)
		if code == "SRT":
			intake_documents.insert(-3, ("Video of Surfactant Administration", "Medical"))
		requirements = {FUND_APPLICATION_FORM: "Mandatory", **intake_requirements}
		for document_type, folder in intake_documents:
			program.append(
				"documents",
				{
					"document_type": document_type,
					"stage": "Intake",
					"folder": folder,
					"requirement": requirements.get(document_type, "Optional"),
				},
			)
		for document_type, requirement in (
			SRT_DISCHARGE_DOCUMENTS if code == "SRT" else GENERAL_DISCHARGE_DOCUMENTS
		):
			program.append(
				"documents",
				{
					"document_type": document_type,
					"stage": "Discharge",
					"folder": "Final",
					"requirement": requirement,
				},
			)
		program.insert()
