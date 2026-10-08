# Copyright (c) 2026, Rahul Agrawal and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from nfi.install import DIRECTOR, SPOC

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = ["User"]


def add_user(email: str, role: str) -> str:
	user = frappe.new_doc("User")
	user.update({"email": email, "first_name": email.split("@")[0], "send_welcome_email": 0})
	user.append("roles", {"role": role})
	user.insert(ignore_permissions=True)
	return user.name


class IntegrationTestNFIHospital(IntegrationTestCase):
	def setUp(self):
		self.spoc = add_user("spoc.member@nfi.test", SPOC)
		self.other_spoc = add_user("spoc.other@nfi.test", SPOC)
		self.director = add_user("director.member@nfi.test", DIRECTOR)
		program = frappe.get_all("NFI Program", pluck="name", limit=1)[0]
		hospital = frappe.new_doc("NFI Hospital")
		hospital.update(
			{
				"hospital_name": "Permission Test Hospital",
				"spocs": [{"user": self.spoc}],
				"programs": [{"program": program, "director": self.director}],
			}
		)
		self.hospital = hospital.insert(ignore_permissions=True).name

	def tearDown(self):
		frappe.db.rollback()

	def get_visible(self, doctype: str, user: str) -> list:
		with self.set_user(user):
			return frappe.get_list(doctype, pluck="name", limit_page_length=0)

	def test_members_list_their_hospital(self):
		self.assertIn(self.hospital, self.get_visible("NFI Hospital", self.spoc))
		self.assertIn(self.hospital, self.get_visible("NFI Hospital", self.director))
		self.assertNotIn(self.hospital, self.get_visible("NFI Hospital", self.other_spoc))

	def test_case_list_runs_for_spoc_and_director(self):
		self.assertEqual(self.get_visible("NFI Case", self.other_spoc), [])
		self.assertEqual(self.get_visible("NFI Case", self.director), [])
