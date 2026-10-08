// Copyright (c) 2026, Rahul Agrawal and contributors
// For license information, please see license.txt

frappe.ui.form.on("NFI Hospital", {
	setup(frm) {
		frm.set_query("user", "spocs", () => get_users_by_role("NFI SPOC"));
		frm.set_query("director", "programs", () => get_users_by_role("NFI Director"));
	},
});

function get_users_by_role(role) {
	return { query: "nfi.api.get_users_by_role", filters: { role } };
}
