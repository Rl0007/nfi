frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["NFI Program Totals"] = {
	method: "nfi.nfi.dashboard_chart_source.nfi_program_totals.nfi_program_totals.get",
	filters: [],
};
