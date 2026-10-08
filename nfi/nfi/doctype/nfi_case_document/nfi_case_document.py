# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NFICaseDocument(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		document_type: DF.Data
		file: DF.Attach | None
		folder: DF.Literal["Medical", "General", "Financial", "Final"]
		is_mandatory: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		requirement: DF.Literal["Mandatory", "Optional", "Mandatory when Out-born"]
		stage: DF.Literal["Intake", "Discharge"]
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Case Document"
