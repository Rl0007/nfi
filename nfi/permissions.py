import frappe
from frappe.query_builder import Criterion

from nfi.install import ACCOUNTANT, ADMIN, COORDINATOR, DIRECTOR, ROLES, SPOC

FULL_ACCESS_ROLES = {COORDINATOR, ACCOUNTANT, ADMIN, "System Manager"}
HIDDEN_FROM_DIRECTOR_STATES = ("Draft", "Information needed")
HOSPITAL_MEMBER_TABLES = {SPOC: ("NFI Hospital SPOC", "user"), DIRECTOR: ("NFI Hospital Program", "director")}


def has_full_access(user: str) -> bool:
	return user == "Administrator" or bool(FULL_ACCESS_ROLES & set(frappe.get_roles(user)))


def has_app_permission() -> bool:
	return frappe.session.user == "Administrator" or bool(
		{*ROLES, "System Manager"} & set(frappe.get_roles())
	)


def get_member_hospitals_query(user: str, role: str = SPOC):
	child_doctype, user_field = HOSPITAL_MEMBER_TABLES[role]
	member = frappe.qb.DocType(child_doctype)
	return (
		frappe.qb.from_(member)
		.select(member.parent)
		.where((member.parenttype == "NFI Hospital") & (member[user_field] == user))
	)


def is_hospital_member(hospital: str, user: str, role: str = SPOC) -> bool:
	child_doctype, user_field = HOSPITAL_MEMBER_TABLES[role]
	return bool(
		frappe.db.exists(child_doctype, {"parenttype": "NFI Hospital", "parent": hospital, user_field: user})
	)


def get_hospital_query_conditions(user: str | None = None, doctype: str | None = None):
	user = user or frappe.session.user
	if has_full_access(user):
		return ""

	hospital = frappe.qb.DocType("NFI Hospital")
	conditions = [
		hospital.name.isin(get_member_hospitals_query(user, role))
		for role in HOSPITAL_MEMBER_TABLES
		if role in frappe.get_roles(user)
	]
	if not conditions:
		return hospital.name.isnull()
	return Criterion.any(conditions)


def has_hospital_permission(doc, ptype: str | None = None, user: str | None = None) -> bool:
	user = user or frappe.session.user
	if has_full_access(user):
		return True
	return any(
		is_hospital_member(doc.name, user, role)
		for role in HOSPITAL_MEMBER_TABLES
		if role in frappe.get_roles(user)
	)


def get_case_query_conditions(user: str | None = None, doctype: str | None = None):
	user = user or frappe.session.user
	if has_full_access(user):
		return ""

	roles = set(frappe.get_roles(user))
	case = frappe.qb.DocType("NFI Case")
	conditions = []
	if SPOC in roles:
		conditions.append(case.hospital.isin(get_member_hospitals_query(user)))
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
		return is_hospital_member(doc.hospital, user)
	return False
