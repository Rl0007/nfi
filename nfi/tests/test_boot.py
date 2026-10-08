import frappe
from frappe.tests import IntegrationTestCase

from nfi.boot import set_home_page
from nfi.install import COORDINATOR, ROLE_HOME_PAGES
from nfi.nfi.doctype.nfi_hospital.test_nfi_hospital import add_user

APP_ROUTE = "/desk/nfi-case"


class IntegrationTestBoot(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def get_bootinfo(self, user: str) -> frappe._dict:
		frappe.set_user(user)
		bootinfo = frappe._dict(app_data=[frappe._dict(app_name="nfi", app_route=APP_ROUTE)])
		set_home_page(bootinfo)
		return bootinfo

	def test_nfi_role_opens_its_workspace(self):
		bootinfo = self.get_bootinfo(add_user("coordinator.home@nfi.test", COORDINATOR))
		self.assertEqual(bootinfo.nfi_home_page, ROLE_HOME_PAGES[COORDINATOR])
		self.assertEqual(bootinfo.app_data[0].app_route, f"/{ROLE_HOME_PAGES[COORDINATOR]}")

	def test_system_manager_keeps_the_generic_desk(self):
		bootinfo = self.get_bootinfo("Administrator")
		self.assertNotIn("nfi_home_page", bootinfo)
		self.assertEqual(bootinfo.app_data[0].app_route, APP_ROUTE)
