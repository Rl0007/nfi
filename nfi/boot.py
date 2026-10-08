import frappe
from frappe.website.utils import get_home_page

from nfi.install import ROLES


def set_home_page(bootinfo):
	roles = set(frappe.get_roles())
	if "System Manager" in roles or not roles.intersection(ROLES):
		return

	home_page = get_home_page().strip("/")
	if not home_page.startswith("desk/"):
		return

	bootinfo.nfi_home_page = home_page
	for app in bootinfo.get("app_data") or []:
		if app.get("app_name") == "nfi":
			app["app_route"] = f"/{home_page}"
