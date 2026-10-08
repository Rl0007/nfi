// Copyright (c) 2026, Rahul Agrawal and contributors
// For license information, please see license.txt

frappe.query_reports["NFI BARP Monthly"] = {
	filters: [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: [...Array(12).keys()].map((index) => ({
				value: String(index + 1),
				label: moment().month(index).format("MMMM"),
			})),
			default: String(moment().month() + 1),
			reqd: 1,
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Int",
			default: moment().year(),
			reqd: 1,
		},
		{
			fieldname: "hospital",
			label: __("Hospital"),
			fieldtype: "Link",
			options: "NFI Hospital",
		},
	],
	tree: true,
	name_field: "row_id",
	parent_field: "parent_row_id",
	initial_depth: 1,
};
