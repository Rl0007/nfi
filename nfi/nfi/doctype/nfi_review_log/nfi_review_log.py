# Copyright (c) 2026, Rahul Agrawal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NFIReviewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		committee: DF.Literal["Medical", "Social", "Financial", "Director", "Accountant"]
		entry_type: DF.Literal["Query", "Response", "Decision", "Note"]
		logged_by: DF.Link | None
		logged_on: DF.Datetime | None
		message: DF.SmallText
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "NFI Review Log"
