# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

from frappe import _
from frappe.utils import date_diff, flt, getdate, today

from nfi.nfi.report.common import (
	get_case_columns,
	get_case_filters,
	get_case_link_column,
	get_cases,
	get_currency_column,
)

UNPAID_STATES = ("Accountant Review", "Payment Processed", "Partially Paid")


def execute(filters: dict | None = None):
	filters = filters or {}
	case_filters = get_case_filters(filters)
	case_filters["workflow_state"] = ["in", UNPAID_STATES]
	if filters.get("due_by"):
		case_filters["payment_due_date"] = ["<=", getdate(filters.get("due_by"))]
	cases = get_cases(
		case_filters,
		[
			"case_number",
			"creation as received_on",
			"baby_name",
			"hospital",
			"program",
			"workflow_state",
			"final_sponsor_amount",
			"total_paid",
			"payment_due_date",
		],
		order_by="payment_due_date asc",
	)
	for case in cases:
		case.balance = flt(case.final_sponsor_amount) - flt(case.total_paid)
		if case.payment_due_date:
			case.days_overdue = max(date_diff(today(), case.payment_due_date), 0)
	return get_columns(), cases


def get_columns() -> list[dict]:
	return [
		*get_case_columns(),
		{"label": _("Status"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 150},
		get_currency_column(_("Final Sponsor Amount"), "final_sponsor_amount"),
		get_currency_column(_("Paid"), "total_paid"),
		get_currency_column(_("Balance"), "balance"),
		{"label": _("Due Date"), "fieldname": "payment_due_date", "fieldtype": "Date", "width": 110},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
		get_case_link_column(),
	]
