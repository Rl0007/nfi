import frappe
from frappe.query_builder.functions import Coalesce, Concat


def execute():
	case = frappe.qb.DocType("NFI Case")
	frappe.qb.update(case).set(case.title, case.baby_name).where(case.case_number.isnull()).run()
	frappe.qb.update(case).set(
		case.title,
		Concat(case.case_number, " – ", Coalesce(case.baby_name, "")),  # noqa: RUF001
	).where(case.case_number.isnotnull()).run()
