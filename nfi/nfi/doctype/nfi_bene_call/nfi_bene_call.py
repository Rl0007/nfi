# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NFIBeneCall(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		call_date: DF.Datetime
		notes: DF.Text | None
		outcome: DF.Literal["Reached - Verified", "Reached - Discrepancy", "Not Reachable", "Call Back"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Bene Call"
