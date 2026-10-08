import frappe
from frappe import _
from frappe.utils import getdate


def get_case_filters(filters: dict) -> dict:
	case_filters = {"case_number": ["is", "set"]}
	if filters.get("from_date") and filters.get("to_date"):
		case_filters["creation"] = [
			"between",
			[getdate(filters.get("from_date")), getdate(filters.get("to_date"))],
		]
	for fieldname in ("hospital", "program"):
		if filters.get(fieldname):
			case_filters[fieldname] = filters.get(fieldname)
	return case_filters


def get_cases(case_filters: dict, fields: list[str], order_by: str = "creation desc") -> list[dict]:
	return frappe.get_list(
		"NFI Case", filters=case_filters, fields=["name", *fields], order_by=order_by, limit_page_length=0
	)


def get_case_columns() -> list[dict]:
	return [
		{"label": _("Case Number"), "fieldname": "case_number", "fieldtype": "Data", "width": 150},
		{"label": _("Received On"), "fieldname": "received_on", "fieldtype": "Date", "width": 110},
		{"label": _("Baby"), "fieldname": "baby_name", "fieldtype": "Data", "width": 180},
		{
			"label": _("Hospital"),
			"fieldname": "hospital",
			"fieldtype": "Link",
			"options": "NFI Hospital",
			"width": 180,
		},
		{
			"label": _("Program"),
			"fieldname": "program",
			"fieldtype": "Link",
			"options": "NFI Program",
			"width": 90,
		},
	]


def get_case_link_column() -> dict:
	return {"label": _("Case"), "fieldname": "name", "fieldtype": "Link", "options": "NFI Case", "width": 120}


def get_currency_column(label: str, fieldname: str) -> dict:
	return {"label": label, "fieldname": fieldname, "fieldtype": "Currency", "width": 130}
