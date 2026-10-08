frappe.provide("nfi");

nfi.INTERNAL_ROLES = ["NFI Coordinator", "NFI Accountant", "NFI Admin", "System Manager"];

nfi.is_spoc_only = () =>
	frappe.user.has_role("NFI SPOC") &&
	!nfi.INTERNAL_ROLES.some((role) => frappe.user.has_role(role));

frappe.listview_settings["NFI Case"] = {
	hide_name_column: true,
	add_fields: ["workflow_state", "spoc_status"],

	get_indicator(doc) {
		if (!doc.workflow_state) return;
		const indicator = frappe.get_indicator(doc, "NFI Case", true);
		if (!nfi.is_spoc_only() || !doc.spoc_status || doc.spoc_status === doc.workflow_state) {
			return indicator;
		}
		return [__(doc.spoc_status), "blue", `spoc_status,=,${doc.spoc_status}`];
	},
};
