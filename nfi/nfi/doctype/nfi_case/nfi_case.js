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
const INTERNAL_ROLES = ["NFI Coordinator", "NFI Accountant", "NFI Admin", "System Manager"];

frappe.ui.form.on("NFI Case", {
	setup(frm) {
		frm.set_query("hospital", () => {
			const is_spoc_only =
				frappe.user.has_role("NFI SPOC") &&
				!INTERNAL_ROLES.some((role) => frappe.user.has_role(role));
			if (!is_spoc_only) return {};
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
			(frm.doc.documents || []).filter((row) => row.file).map((row) => [row.document_type, row.file]),
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
		const { message } = await frappe.db.get_value("NFI Case", frm.doc.original_case, TOPUP_COPY_FIELDS);
		await frm.set_value(message);
		frm.trigger("mother_name");
	},
});

async function set_hospital_programs(frm) {
	frm.hospital_programs = [];
	if (!frm.doc.hospital) return;
	const hospital = await frappe.db.get_doc("NFI Hospital", frm.doc.hospital);
	frm.hospital_programs = hospital.programs.map((row) => row.program);
}

function is_required(frm, requirement) {
	return (
		requirement === "Mandatory" ||
		(requirement === "Mandatory when Out-born" && frm.doc.birth_status === "Out-born")
	) ? 1 : 0;
}
