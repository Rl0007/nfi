# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NFIProgram(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from nfi.nfi.doctype.nfi_program_document.nfi_program_document import NFIProgramDocument

		description: DF.SmallText | None
		documents: DF.Table[NFIProgramDocument]
		fixed_amount: DF.Currency
		program_name: DF.Data
		review_route: DF.Literal["Medical, Social & Financial", "Medical", "Director Only"]
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Program"
