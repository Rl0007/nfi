# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from nfi.install import DIRECTOR, SPOC


class NFIHospital(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from nfi.nfi.doctype.nfi_hospital_program.nfi_hospital_program import NFIHospitalProgram
		from nfi.nfi.doctype.nfi_hospital_spoc.nfi_hospital_spoc import NFIHospitalSPOC

		city: DF.Data | None
		hospital_name: DF.Data
		mou_expiry_date: DF.Date | None
		mou_file: DF.Attach | None
		nicu_beds: DF.Int
		programs: DF.Table[NFIHospitalProgram]
		spocs: DF.Table[NFIHospitalSPOC]
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Hospital"

	def validate(self):
		for table_field, user_field, role in (("spocs", "user", SPOC), ("programs", "director", DIRECTOR)):
			for row in self.get(table_field):
				user = row.get(user_field)
				if user and role not in frappe.get_roles(user):
					frappe.throw(_("Row {0}: {1} does not have the {2} role.").format(row.idx, user, role))
