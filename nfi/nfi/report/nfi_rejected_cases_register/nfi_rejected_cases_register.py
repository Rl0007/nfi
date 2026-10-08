# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

from frappe import _

from nfi.nfi.report.common import (
	get_case_columns,
	get_case_filters,
	get_case_link_column,
	get_cases,
	get_currency_column,
)


def execute(filters: dict | None = None):
	case_filters = get_case_filters(filters or {})
	case_filters["workflow_state"] = "Rejected"
	data = get_cases(
		case_filters,
		[
			"case_number",
			"creation as received_on",
			"baby_name",
			"hospital",
			"program",
			"hospital_estimate",
			"director_decision",
			"rejection_reason",
		],
	)
	return get_columns(), data


def get_columns() -> list[dict]:
	return [
		*get_case_columns(),
		get_currency_column(_("Hospital Estimate"), "hospital_estimate"),
		{
			"label": _("Director Decision"),
			"fieldname": "director_decision",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Rejection Reason"),
			"fieldname": "rejection_reason",
			"fieldtype": "Small Text",
			"width": 300,
		},
		get_case_link_column(),
	]
