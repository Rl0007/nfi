// Copyright (c) 2026, Rahul Agrawal and contributors
// For license information, please see license.txt

frappe.query_reports["NFI Payments Due"] = {
	filters: [
		{
			fieldname: "due_by",
			label: __("Due By"),
			fieldtype: "Date",
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
