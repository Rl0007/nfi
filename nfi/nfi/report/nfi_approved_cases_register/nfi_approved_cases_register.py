# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

from frappe import _

from nfi.nfi.doctype.nfi_case.nfi_case import TOPUP_ELIGIBLE_STATES as APPROVED_STATES
from nfi.nfi.report.common import (
	get_case_columns,
	get_case_filters,
	get_case_link_column,
	get_cases,
	get_currency_column,
)

AMOUNT_FIELDS = (
	"hospital_estimate",
	"recommended_amount",
	"director_approved_amount",
	"final_sponsor_amount",
	"total_paid",
)


def execute(filters: dict | None = None):
	case_filters = get_case_filters(filters or {})
	case_filters["workflow_state"] = ["in", APPROVED_STATES]
	data = get_cases(
		case_filters,
		[
			"case_number",
			"creation as received_on",
			"baby_name",
			"hospital",
			"program",
			"case_type",
			"workflow_state",
			*AMOUNT_FIELDS,
		],
	)
	return get_columns(), data


def get_columns() -> list[dict]:
	return [
		*get_case_columns(),
		{"label": _("Case Type"), "fieldname": "case_type", "fieldtype": "Data", "width": 100},
		get_currency_column(_("Hospital Estimate"), "hospital_estimate"),
		get_currency_column(_("Recommended"), "recommended_amount"),
		get_currency_column(_("Director Approved"), "director_approved_amount"),
		get_currency_column(_("Final Sponsor Amount"), "final_sponsor_amount"),
		get_currency_column(_("Paid"), "total_paid"),
		{"label": _("Status"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 200},
		get_case_link_column(),
	]
