// Copyright (c) 2026, Rahul Agrawal and contributors
// For license information, please see license.txt

frappe.query_reports["NFI Rejected Cases Register"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.year_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "hospital",
			label: __("Hospital"),
			fieldtype: "Link",
			options: "NFI Hospital",
		},
		{
			fieldname: "program",
			label: __("Program"),
			fieldtype: "Link",
			options: "NFI Program",
		},
	],
};
