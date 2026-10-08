import frappe
from frappe.query_builder import Criterion

from nfi.install import ACCOUNTANT, ADMIN, COORDINATOR, DIRECTOR, SPOC

FULL_ACCESS_ROLES = {COORDINATOR, ACCOUNTANT, ADMIN, "System Manager"}
HIDDEN_FROM_DIRECTOR_STATES = ("Draft", "Information needed")


def has_full_access(user: str) -> bool:
	return user == "Administrator" or bool(FULL_ACCESS_ROLES & set(frappe.get_roles(user)))


def get_spoc_hospitals_query(user: str):
	hospital_spoc = frappe.qb.DocType("NFI Hospital SPOC")
	return (
		frappe.qb.from_(hospital_spoc)
		.select(hospital_spoc.parent)
		.where((hospital_spoc.parenttype == "NFI Hospital") & (hospital_spoc.user == user))
	)


def is_hospital_spoc(hospital: str, user: str) -> bool:
	return bool(
		frappe.db.exists(
			"NFI Hospital SPOC", {"parenttype": "NFI Hospital", "parent": hospital, "user": user}
		)
	)


def get_case_query_conditions(user: str | None = None, doctype: str | None = None):
	user = user or frappe.session.user
	if has_full_access(user):
		return ""

	roles = set(frappe.get_roles(user))
	case = frappe.qb.DocType("NFI Case")
	conditions = []
	if SPOC in roles:
		conditions.append(case.hospital.isin(get_spoc_hospitals_query(user)))
		conditions.append(case.hospital.isnull() & (case.owner == user))
	if DIRECTOR in roles:
		conditions.append((case.director == user) & case.workflow_state.notin(HIDDEN_FROM_DIRECTOR_STATES))
	if not conditions:
		return case.name.isnull()
	return Criterion.any(conditions)


def has_case_permission(doc, ptype: str | None = None, user: str | None = None) -> bool:
	user = user or frappe.session.user
	if has_full_access(user):
		return True

	roles = set(frappe.get_roles(user))
	if (
		DIRECTOR in roles
		and doc.get("director") == user
		and doc.get("workflow_state") not in HIDDEN_FROM_DIRECTOR_STATES
	):
		return True
	if SPOC in roles:
		if not doc.get("hospital"):
			return doc.is_new() or doc.owner == user
		return is_hospital_spoc(doc.hospital, user)
	return False
