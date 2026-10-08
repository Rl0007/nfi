# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NFIPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		mode: DF.Literal["NEFT", "RTGS", "IMPS", "Cheque", "Other"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payment_date: DF.Date
		reference: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Payment"
