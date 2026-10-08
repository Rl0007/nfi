import frappe

from nfi.install import APPROVED_AWAITING_DOCUMENTS


def send_case_outcome_email(doc, method=None):
	if not doc.has_value_changed("workflow_state"):
		return

	template_name = get_outcome_template(doc)
	if not template_name:
		return

	recipients = get_hospital_spoc_emails(doc.hospital)
	if not recipients:
		return

	template = frappe.get_cached_doc("Email Template", template_name)
	context = doc.as_dict()
	try:
		frappe.sendmail(
			recipients=recipients,
			subject=template.get_formatted_subject(context),
			message=template.get_formatted_response(context),
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)
	except frappe.OutgoingEmailError:
		# A missing outgoing Email Account must not block the approval or rejection itself.
		frappe.log_error(
			f"{template_name} not sent for {doc.case_number}",
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)


def get_outcome_template(doc) -> str | None:
	if doc.workflow_state == "Rejected":
		return "NFI Rejection"
	if doc.workflow_state == APPROVED_AWAITING_DOCUMENTS:
		return "NFI SRT Approval" if doc.program == "SRT" else "NFI Hospital Approval"


def get_hospital_spoc_emails(hospital: str | None) -> list[str]:
	if not hospital:
		return []
	spoc_users = frappe.get_all(
		"NFI Hospital SPOC",
		filters={"parenttype": "NFI Hospital", "parent": hospital},
		pluck="user",
	)
	if not spoc_users:
		return []
	return frappe.get_all("User", filters={"name": ["in", spoc_users], "enabled": 1}, pluck="email")
