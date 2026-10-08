# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

from itertools import groupby

from frappe import _
from frappe.utils import cint, flt, get_last_day, getdate

from nfi.nfi.report.common import (
	get_case_columns,
	get_case_filters,
	get_case_link_column,
	get_cases,
	get_currency_column,
)

AMOUNT_FIELDS = ("hospital_estimate", "director_approved_amount", "final_sponsor_amount", "total_paid")


def execute(filters: dict | None = None):
	filters = filters or {}
	from_date = getdate(f"{cint(filters.get('year'))}-{cint(filters.get('month')):02d}-01")
	case_filters = get_case_filters(
		{"from_date": from_date, "to_date": get_last_day(from_date), "hospital": filters.get("hospital")}
	)
	case_filters["program"] = "BARP"
	cases = get_cases(
		case_filters,
		[
			"case_number",
			"creation as received_on",
			"baby_name",
			"hospital",
			"program",
			"workflow_state",
			*AMOUNT_FIELDS,
		],
		order_by="hospital asc, creation asc",
	)
	return get_columns(), get_hospital_rows(cases)


def get_hospital_rows(cases: list[dict]) -> list[dict]:
	data = []
	for hospital, hospital_cases in groupby(cases, key=lambda case: case.hospital):
		hospital_cases = list(hospital_cases)
		hospital_row = {
			"row_id": hospital,
			"case_number": hospital,
			"hospital": hospital,
			"indent": 0,
			"case_count": len(hospital_cases),
		}
		for fieldname in AMOUNT_FIELDS:
			hospital_row[fieldname] = sum(flt(case.get(fieldname)) for case in hospital_cases)
		data.append(hospital_row)
		data.extend(
			{**case, "row_id": case.name, "parent_row_id": hospital, "indent": 1} for case in hospital_cases
		)
	return data


def get_columns() -> list[dict]:
	return [
		*get_case_columns(),
		{"label": _("Cases"), "fieldname": "case_count", "fieldtype": "Int", "width": 70},
		{"label": _("Status"), "fieldname": "workflow_state", "fieldtype": "Data", "width": 200},
		get_currency_column(_("Hospital Estimate"), "hospital_estimate"),
		get_currency_column(_("Director Approved"), "director_approved_amount"),
		get_currency_column(_("Final Sponsor Amount"), "final_sponsor_amount"),
		get_currency_column(_("Paid"), "total_paid"),
		get_case_link_column(),
	]
