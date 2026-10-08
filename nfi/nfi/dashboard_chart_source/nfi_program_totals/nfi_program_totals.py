import frappe


@frappe.whitelist()
def get(chart_name: str, filters: str | list | None = None) -> dict:
	chart = frappe.get_cached_doc("Dashboard Chart", chart_name)
	total = (
		{"SUM": chart.aggregate_function_based_on, "as": "total"}
		if chart.aggregate_function_based_on
		else {"COUNT": "*", "as": "total"}
	)
	filters = frappe.parse_json(filters) or frappe.parse_json(chart.filters_json) or []
	rows = frappe.get_list(
		"NFI Case",
		fields=["program", total],
		filters=[*filters, ["NFI Case", "program", "is", "set"]],
		group_by="program",
		order_by="total desc",
	)
	return {
		"labels": [row.program for row in rows],
		"datasets": [{"name": chart.chart_name, "values": [row.total for row in rows]}],
	}
