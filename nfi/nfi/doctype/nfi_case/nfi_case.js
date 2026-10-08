// Copyright (c) 2026, Rahul Agrawal and contributors
// For license information, please see license.txt

const TOPUP_COPY_FIELDS = [
	"hospital",
	"mother_name",
	"mother_mobile",
	"father_name",
	"father_mobile",
	"gender",
	"birth_status",
];
const TOPUP_ELIGIBLE_STATES = [
	"Approved – Awaiting Final Discharge Documents",
	"Accountant Review",
	"Payment Processed",
	"Partially Paid",
	"Paid",
	"Closed",
];

const DIRECTOR_EDITOR_ROLES = ["NFI Coordinator", "NFI Admin", "System Manager"];

frappe.ui.form.on("NFI Case", {
	setup(frm) {
		frm.set_query("hospital", () => {
			if (!nfi.is_spoc_only()) return {};
			return { filters: [["NFI Hospital SPOC", "user", "=", frappe.session.user]] };
		});
		frm.set_query("program", () => ({
			filters: { name: ["in", frm.hospital_programs || []] },
		}));
		frm.set_query("original_case", () => ({
			filters: { workflow_state: ["in", TOPUP_ELIGIBLE_STATES], name: ["!=", frm.doc.name] },
		}));
	},

	async refresh(frm) {
		frm.set_df_property("original_case", "filter_description", __("Approved cases only"));
		const needs_information =
			frm.doc.workflow_state === "Information needed" && frm.doc.return_reason;
		frm.set_intro(
			needs_information
				? __("NFI needs more information: {0}", [
						frappe.utils.escape_html(frm.doc.return_reason),
				  ])
				: "",
			"orange"
		);
		if (!frm.is_new() && frappe.user.has_role(DIRECTOR_EDITOR_ROLES)) {
			frm.add_custom_button(__("Change Director"), () => change_director(frm));
		}
		await set_hospital_programs(frm);
	},

	async hospital(frm) {
		await set_hospital_programs(frm);
		if (frm.doc.program && !frm.hospital_programs.includes(frm.doc.program)) {
			frm.set_value("program", null);
		}
	},

	async program(frm) {
		if (!frm.doc.program) return;
		const program = await frappe.db.get_doc("NFI Program", frm.doc.program);
		const files = Object.fromEntries(
			(frm.doc.documents || [])
				.filter((row) => row.file)
				.map((row) => [row.document_type, row.file])
		);
		frm.clear_table("documents");
		for (const row of program.documents) {
			frm.add_child("documents", {
				document_type: row.document_type,
				stage: row.stage,
				folder: row.folder,
				requirement: row.requirement,
				is_mandatory: is_required(frm, row.requirement),
				file: files[row.document_type],
			});
		}
		frm.refresh_field("documents");
	},

	birth_status(frm) {
		for (const row of frm.doc.documents || []) {
			row.is_mandatory = is_required(frm, row.requirement);
		}
		frm.refresh_field("documents");
	},

	mother_name(frm) {
		frm.set_value("baby_name", frm.doc.mother_name ? `B/O ${frm.doc.mother_name}` : "");
	},

	async original_case(frm) {
		if (!frm.doc.original_case) return;
		const { message } = await frappe.db.get_value(
			"NFI Case",
			frm.doc.original_case,
			TOPUP_COPY_FIELDS
		);
		await frm.set_value(message);
		frm.trigger("mother_name");
	},
});

async function set_hospital_programs(frm) {
	frm.hospital_programs = [];
	// a reassigned director may not be able to read the hospital
	if (!frm.doc.hospital || !frappe.user.has_role(["NFI SPOC", ...nfi.INTERNAL_ROLES])) return;
	const hospital = await frappe.db.get_doc("NFI Hospital", frm.doc.hospital);
	frm.hospital_programs = hospital.programs.map((row) => row.program);
}

function is_required(frm, requirement) {
	return requirement === "Mandatory" ||
		(requirement === "Mandatory when Out-born" && frm.doc.birth_status === "Out-born")
		? 1
		: 0;
}

function change_director(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Change Director"),
		fields: [
			{
				fieldname: "director",
				fieldtype: "Link",
				options: "User",
				label: __("Director"),
				reqd: 1,
				default: frm.doc.director,
				get_query: () => ({
					query: "nfi.api.get_users_by_role",
					filters: { role: "NFI Director" },
				}),
			},
		],
		primary_action_label: __("Change"),
		primary_action: async ({ director }) => {
			await frm.call("change_director", { director });
			dialog.hide();
			await frm.reload_doc();
		},
	});
	dialog.show();
}
