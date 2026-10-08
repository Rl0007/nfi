# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, today

from nfi.install import (
	APPROVED_AWAITING_DOCUMENTS,
	BOTH_PARENTS_AADHAAR,
	FATHER_AADHAAR,
	MOTHER_AADHAAR,
	SPOC,
)
from nfi.permissions import has_full_access, is_hospital_member

REQUIRED_INTAKE_FIELDS = (
	"case_type",
	"hospital",
	"program",
	"mother_name",
	"mother_mobile",
	"father_name",
	"father_mobile",
	"gender",
	"birth_status",
)
INTAKE_FIELDS = (*REQUIRED_INTAKE_FIELDS, "original_case")
PARENT_NAME_FIELDS = ("mother_name", "father_name")
SPOC_EDITABLE_STATES = ("Draft", "Information needed")
PASS_THROUGH_STATES = {
	"Submitted for Processing": "Coordinator Verification",
	"Director Approved": "Coordinator Review",
	"Director Rejected": "Coordinator Review",
}
INTERNAL_STATES = {
	"Medical Review",
	"Social & Financial Review",
	"Director Review",
	"Director Approved",
	"Director Rejected",
	"Accountant Review",
}
TOPUP_ELIGIBLE_STATES = (
	APPROVED_AWAITING_DOCUMENTS,
	"Accountant Review",
	"Payment Processed",
	"Partially Paid",
	"Paid",
	"Closed",
)
PAYMENT_STATES = ("Payment Processed", "Partially Paid")


class NFICase(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from nfi.nfi.doctype.nfi_bene_call.nfi_bene_call import NFIBeneCall
		from nfi.nfi.doctype.nfi_case_document.nfi_case_document import NFICaseDocument
		from nfi.nfi.doctype.nfi_payment.nfi_payment import NFIPayment
		from nfi.nfi.doctype.nfi_review_log.nfi_review_log import NFIReviewLog

		approved_topup: DF.Currency
		baby_name: DF.Data | None
		bene_calls: DF.Table[NFIBeneCall]
		birth_status: DF.Literal["", "In-born", "Out-born"]
		case_number: DF.Data | None
		case_type: DF.Literal["Fresh Case", "Top-up"]
		director: DF.Link | None
		director_approved_amount: DF.Currency
		director_decision: DF.Literal["", "Approved", "Rejected"]
		discharge_or_death_date: DF.Date | None
		documents: DF.Table[NFICaseDocument]
		fa_advance_paid_by_family: DF.Data | None
		fa_approval_date: DF.Data | None
		fa_approval_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_baby_date_of_birth: DF.Data | None
		fa_baby_or_beneficiary_name: DF.Data | None
		fa_bank_statement_and_meeting_consent_name: DF.Data | None
		fa_bank_statement_and_meeting_consent_signature_present: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		fa_bank_statement_last_six_months: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_beneficiary_details_additional_fields: DF.SmallText | None
		fa_birth_weight: DF.Data | None
		fa_current_outstanding_bill: DF.Data | None
		fa_date_of_marriage: DF.Data | None
		fa_declarant_name: DF.Data | None
		fa_declaration_date: DF.Data | None
		fa_declaration_of_beneficiary_additional_fields: DF.SmallText | None
		fa_delivery_charges: DF.Data | None
		fa_designation: DF.Data | None
		fa_doctor_name: DF.Data | None
		fa_doctor_name_filled: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_doctor_signoff_complete: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_employment_and_financial_details_additional_fields: DF.SmallText | None
		fa_estimated_nicu_stay: DF.Data | None
		fa_family_details_additional_fields: DF.SmallText | None
		fa_father_address: DF.Data | None
		fa_father_assets_land_or_house: DF.Data | None
		fa_father_company_or_employer: DF.Data | None
		fa_father_contact_number: DF.Data | None
		fa_father_date_of_birth: DF.Data | None
		fa_father_education: DF.Data | None
		fa_father_monthly_or_daily_wages: DF.Data | None
		fa_father_name: DF.Data | None
		fa_father_occupation: DF.Data | None
		fa_gender: DF.Data | None
		fa_gestational_age: DF.Data | None
		fa_gravida: DF.Data | None
		fa_hospital_approval_additional_fields: DF.SmallText | None
		fa_inborn_or_outborn: DF.Data | None
		fa_income_proof_additional_fields: DF.SmallText | None
		fa_information_truth_declaration_present: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		fa_information_truth_signature_present: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		fa_medical_details_additional_fields: DF.SmallText | None
		fa_mother_address: DF.Data | None
		fa_mother_assets_land_or_house: DF.Data | None
		fa_mother_company_or_employer: DF.Data | None
		fa_mother_contact_number: DF.Data | None
		fa_mother_date_of_birth: DF.Data | None
		fa_mother_education: DF.Data | None
		fa_mother_monthly_or_daily_wages: DF.Data | None
		fa_mother_name: DF.Data | None
		fa_mother_occupation: DF.Data | None
		fa_nicu_admission_date: DF.Data | None
		fa_number_of_family_members: DF.Int
		fa_other_income_proof: DF.Data | None
		fa_other_support_received: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_other_support_source_or_details: DF.Data | None
		fa_outborn_hospital_name: DF.Data | None
		fa_parent_name: DF.Data | None
		fa_parent_name_filled: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_parent_signature_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_parent_signoff_complete: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_photo_and_video_consent_name: DF.Data | None
		fa_photo_and_video_consent_signature_present: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		fa_signature_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_stamp_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_tahsildar_income_certificate: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		fa_time_of_birth: DF.Data | None
		fa_total_estimated_hospital_bill: DF.Data | None
		fa_type_of_conception: DF.Data | None
		fa_type_of_delivery: DF.Data | None
		father_mobile: DF.Data | None
		father_name: DF.Data | None
		final_bill: DF.Currency
		final_documents_received_date: DF.Date | None
		final_sponsor_amount: DF.Currency
		financial_status: DF.Literal["", "Pending", "Query Raised", "Approved", "Rejected"]
		gender: DF.Literal["", "Male", "Female", "Other"]
		has_topup: DF.Check
		hospital: DF.Link | None
		hospital_estimate: DF.Currency
		interim_abortions: DF.Int
		interim_age_years: DF.Int
		interim_antenatal_risk_factors: DF.SmallText | None
		interim_apgar_score: DF.Data | None
		interim_baby_details_additional_fields: DF.SmallText | None
		interim_birth_weight_grams: DF.Int
		interim_case_summary: DF.SmallText | None
		interim_corrected_gestational_age: DF.Data | None
		interim_cpap: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_current_status_additional_fields: DF.SmallText | None
		interim_date_of_birth: DF.Data | None
		interim_day_of_life: DF.Data | None
		interim_diagnosis_feeding_intolerance: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_diagnosis_hypoglycemia: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_diagnosis_low_birth_weight: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_diagnosis_necrotizing_enterocolitis: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_diagnosis_neonatal_hyperbilirubinemia: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_diagnosis_others: DF.Data | None
		interim_diagnosis_patent_ductus_arteriosus: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_diagnosis_prematurity: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_diagnosis_respiratory_distress_syndrome: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_diagnosis_sepsis: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_diagnosis_transient_tachypnea_of_the_newborn: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_gender: DF.Data | None
		interim_gestational_age: DF.Data | None
		interim_gravida: DF.Int
		interim_hhfnc: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_inborn: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_inotropes_no: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_inotropes_yes: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_investigations_attached_labs: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_investigations_attached_others: DF.Data | None
		interim_investigations_attached_scans: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_investigations_attached_x_ray: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_iui: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_iv_antibiotics_no: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_iv_antibiotics_yes: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_ivf: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_living_children: DF.Int
		interim_married_life_years: DF.Int
		interim_maternal_details_additional_fields: DF.SmallText | None
		interim_mechanical_ventilation: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_name: DF.Data | None
		interim_natural_conception: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_ongoing_treatment_feeding_direct_breastfeeding: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_feeding_nothing_by_mouth: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_feeding_orogastric_feeding: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_feeding_palada: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_others: DF.Data | None
		interim_ongoing_treatment_respiration_cpap: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_respiration_hfnc: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_respiration_mechanical_ventilation: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_ongoing_treatment_respiration_oxygen: DF.Literal[
			"", "checked", "unchecked", "unclear", "not present"
		]
		interim_others: DF.Data | None
		interim_outborn: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_oxygen: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_para: DF.Int
		interim_place_of_birth: DF.Data | None
		interim_plan_of_discharge: DF.SmallText | None
		interim_remarks: DF.SmallText | None
		interim_signature_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_signing_doctor_name: DF.Data | None
		interim_stamp_present: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_time_of_birth: DF.Data | None
		interim_today_s_weight_grams: DF.Int
		interim_tpn_no: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_tpn_yes: DF.Literal["", "checked", "unchecked", "unclear", "not present"]
		interim_treatment_given_additional_fields: DF.SmallText | None
		is_topup: DF.Check
		medical_status: DF.Literal["", "Pending", "Query Raised", "Approved", "Rejected"]
		mortality: DF.Check
		mortality_date: DF.Date | None
		mother_mobile: DF.Data | None
		mother_name: DF.Data | None
		original_case: DF.Link | None
		payment_due_date: DF.Date | None
		payments: DF.Table[NFIPayment]
		post_discharge_photo_status: DF.Literal["", "Received", "Not Received"]
		program: DF.Link | None
		recommended_amount: DF.Currency
		rejection_reason: DF.SmallText | None
		requested_topup: DF.Currency
		return_reason: DF.SmallText | None
		review_log: DF.Table[NFIReviewLog]
		review_route: DF.Data | None
		social_status: DF.Literal["", "Pending", "Query Raised", "Approved", "Rejected"]
		spoc_status: DF.Data | None
		srt_vials: DF.Int
		title: DF.Data | None
		total_paid: DF.Currency
		video_testimonial_status: DF.Literal["", "Pending", "Requested", "Received", "Declined"]
		workflow_state: DF.Link | None
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Case"

	def validate(self):
		previous_state = "Draft" if self.is_new() else self.get_doc_before_save().workflow_state
		if self.is_spoc_only():
			self.validate_spoc_changes(previous_state)
		self.baby_name = f"B/O {self.mother_name}" if self.mother_name else None
		self.is_topup = self.case_type == "Top-up"
		if not self.is_topup:
			self.original_case = None
		self.set_hospital_program()
		self.set_documents()
		self.total_paid = sum(flt(row.amount) for row in self.payments)
		state = self.workflow_state or "Draft"
		if state != previous_state:
			self.validate_transition(previous_state)
		self.spoc_status = get_spoc_status(state)
		self.title = get_case_title(self.case_number, self.baby_name)

	def on_update(self):
		if self.flags.mark_original_topup:
			frappe.db.set_value("NFI Case", self.original_case, "has_topup", 1)
		self.set_automatic_state()

	def on_trash(self):
		if self.flags.ignore_permissions:
			return
		if self.case_number or (self.workflow_state or "Draft") != "Draft":
			frappe.throw(_("Only Draft cases without a Case Number can be deleted."))

	def is_spoc_only(self) -> bool:
		user = frappe.session.user
		return SPOC in frappe.get_roles(user) and not has_full_access(user)

	def validate_spoc_changes(self, previous_state: str):
		if self.is_new():
			return
		if previous_state not in SPOC_EDITABLE_STATES:
			if any(self.has_value_changed(fieldname) for fieldname in INTAKE_FIELDS):
				frappe.throw(_("Intake details can only be edited in Draft or Information needed."))
			if previous_state != APPROVED_AWAITING_DOCUMENTS and self.get_document_files() != (
				self.get_doc_before_save().get_document_files()
			):
				frappe.throw(_("Documents cannot be changed in status {0}.").format(_(previous_state)))
		if self.case_number and any(self.has_value_changed(fieldname) for fieldname in PARENT_NAME_FIELDS):
			frappe.throw(_("Parent names cannot be changed after submission. Ask the NFI Coordinator."))

	def get_document_files(self) -> list[tuple]:
		return [(row.document_type, row.file) for row in self.documents]

	def set_hospital_program(self):
		if self.hospital and self.is_spoc_only() and self.has_value_changed("hospital"):
			if not is_hospital_member(self.hospital, frappe.session.user):
				frappe.throw(_("You are not a SPOC of hospital {0}.").format(self.hospital))
		if not (self.hospital and self.program):
			return
		if not (self.has_value_changed("hospital") or self.has_value_changed("program") or not self.director):
			return
		mapping = frappe.get_all(
			"NFI Hospital Program",
			filters={"parenttype": "NFI Hospital", "parent": self.hospital, "program": self.program},
			fields=["director"],
			limit=1,
		)
		if not mapping:
			frappe.throw(
				_("Program {0} is not enabled for hospital {1}.").format(self.program, self.hospital)
			)
		self.director = mapping[0].director

	def set_documents(self):
		if self.program and not self.documents:
			for row in get_program_documents(self.program):
				self.append("documents", row)
		for row in self.documents:
			row.is_mandatory = self.is_required(row.requirement)

	def is_required(self, requirement: str | None) -> bool:
		return requirement == "Mandatory" or (
			requirement == "Mandatory when Out-born" and self.birth_status == "Out-born"
		)

	def validate_transition(self, previous_state: str):
		if previous_state in SPOC_EDITABLE_STATES:
			self.validate_intake()
			if not self.case_number:
				self.case_number = make_autoname(
					"TP-.YYYY.-.#####" if self.is_topup else "NFI-.YYYY.-.#####", "NFI Case", self
				)
				self.flags.mark_original_topup = self.is_topup

		state = self.workflow_state
		returned_by_accountant = previous_state == "Accountant Review" and state == "Coordinator Review"
		is_return = state == "Information needed" or returned_by_accountant
		if is_return and not self.return_reason:
			frappe.throw(_("Enter a Return Reason before returning the case."))
		if not is_return:
			# so the next return cannot reuse a reason written for an earlier one
			self.return_reason = None
		if state == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Enter a Rejection Reason before rejecting the case."))
		if state == "Director Review" and not self.director:
			frappe.throw(_("No Director is mapped for this hospital and program."))
		if state == "Accountant Review":
			self.validate_documents("Discharge")
			self.final_documents_received_date = self.final_documents_received_date or today()
		if state == "Payment Processed" and flt(self.final_sponsor_amount) <= 0:
			frappe.throw(_("Enter the Final Sponsor Amount before processing payment."))

	def validate_intake(self):
		missing = [
			self.meta.get_label(fieldname) for fieldname in REQUIRED_INTAKE_FIELDS if not self.get(fieldname)
		]
		if self.is_topup and not self.original_case:
			missing.append(self.meta.get_label("original_case"))
		if missing:
			frappe.throw(_("Complete these fields before submitting: {0}").format(", ".join(missing)))
		if self.is_topup:
			self.validate_original_case()
		self.validate_documents("Intake")

	def validate_original_case(self):
		original_state = frappe.db.get_value("NFI Case", self.original_case, "workflow_state")
		if self.original_case == self.name or original_state not in TOPUP_ELIGIBLE_STATES:
			frappe.throw(_("Case {0} is not eligible for a top-up.").format(self.original_case))

	def validate_documents(self, stage: str):
		uploaded = {row.document_type for row in self.documents if row.file}
		if BOTH_PARENTS_AADHAAR in uploaded:
			uploaded |= {FATHER_AADHAAR, MOTHER_AADHAAR}
		missing = [
			row.document_type
			for row in get_program_documents(self.program, stage)
			if self.is_required(row.requirement) and row.document_type not in uploaded
		]
		if missing:
			frappe.throw(_("Upload these mandatory {0} documents: {1}").format(_(stage), ", ".join(missing)))

	def set_automatic_state(self):
		# Frappe validates workflow transitions after the controller's validate, so system-driven
		# moves are written after save instead of through the workflow.
		state = PASS_THROUGH_STATES.get(self.workflow_state, self.workflow_state)
		if state in PAYMENT_STATES and self.total_paid > 0:
			state = "Paid" if self.total_paid >= flt(self.final_sponsor_amount) else "Partially Paid"
		if state != self.workflow_state:
			self.db_set({"workflow_state": state, "spoc_status": get_spoc_status(state)})


def get_case_title(case_number: str | None, baby_name: str | None) -> str | None:
	return " – ".join(part for part in (case_number, baby_name) if part) or None  # noqa: RUF001


def get_spoc_status(state: str) -> str:
	return "Processing" if state in INTERNAL_STATES else state


def get_program_documents(program: str, stage: str | None = None) -> list[dict]:
	filters = {"parenttype": "NFI Program", "parent": program}
	if stage:
		filters["stage"] = stage
	return frappe.get_all(
		"NFI Program Document",
		filters=filters,
		fields=["document_type", "stage", "folder", "requirement"],
		order_by="idx",
	)
