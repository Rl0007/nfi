// The desk root shows the generic desktop; an NFI user's root is their role's workspace instead.
if (frappe.boot.nfi_home_page) {
	frappe.re_route[""] = frappe.boot.nfi_home_page;
}
