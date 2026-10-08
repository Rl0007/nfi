frappe.pages["nfi-payments"].on_page_load = async (wrapper) => {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Payments"),
		single_column: true,
	});
	await frappe.require("/assets/nfi/js/nfi_case_list.js");
	wrapper.payments = new Payments(page);
	wrapper.payments.refresh();
};

frappe.pages["nfi-payments"].on_page_show = (wrapper) => wrapper.payments?.refresh();

const PAYMENT_STATES = ["Accountant Review", "Payment Processed", "Partially Paid", "Paid"];

class Payments {
	constructor(page) {
		this.page = page;
		this.state = null;
		this.filters = nfi.desk.add_case_filters(page, () => this.refresh());
		this.table = new nfi.desk.CaseTable({
			method: "nfi.api.get_payment_list",
			get_args: () => this.get_filters(),
			on_page: (result) => this.set_summary(result),
			empty_title: __("No cases in payment"),
			columns: this.get_columns(),
		});
		const body = $('<div class="px-3 pt-3 pb-4"></div>').appendTo(page.main);
		this.summary = $(`<div class="frappe-card shadow-none p-4 mb-3">
			<div class="row nfi-payment-stats"></div>
		</div>`).appendTo(body);
		this.summary.find(".nfi-payment-stats").html(
			Array.from(
				{ length: 4 },
				() =>
					`<div class="col-6 col-md-3">${frappe.ui.skeleton.html({
						height: "44px",
					})}</div>`
			).join("")
		);
		this.add_state_buttons(body);
		body.append(this.table.wrapper);
	}

	add_state_buttons(parent) {
		const state_buttons = new frappe.ui.TabButtons({
			label: __("Payment status"),
			options: [
				{ label: __("All"), value: "" },
				...PAYMENT_STATES.map((state) => ({ label: __(state), value: state })),
			],
			value: "",
			on_change: (value) => {
				this.state = value || null;
				this.refresh();
			},
		});
		$('<div class="flex items-center justify-between mb-3"></div>')
			.append(
				$('<div class="text-base-semibold text-ink-gray-8"></div>').text(
					__("Cases in payment")
				),
				state_buttons.$el
			)
			.appendTo(parent);
	}

	get_columns() {
		const escape = frappe.utils.escape_html;
		return [
			{ label: __("Case"), format: nfi.desk.format_case, skeleton_height: "32px" },
			{ label: __("Hospital"), format: (row) => escape(row.hospital || "") },
			{ label: __("Program"), format: (row) => nfi.desk.format_program(row.program) },
			{ label: __("Status"), format: (row) => nfi.desk.format_state(row.workflow_state) },
			{ label: __("Due"), format: (row) => this.format_due_date(row) },
			{
				label: __("Sponsor Amount"),
				align: "right",
				format: (row) => nfi.desk.format_money(row.final_sponsor_amount),
			},
			{
				label: __("Paid"),
				align: "right",
				format: (row) => nfi.desk.format_money(row.total_paid),
			},
			{
				label: __("Balance"),
				align: "right",
				format: (row) =>
					`<span class="text-base-medium text-ink-gray-8">${nfi.desk.format_money(
						row.balance
					)}</span>`,
			},
		];
	}

	format_due_date(row) {
		if (!row.payment_due_date)
			return `<span class="text-sm text-ink-gray-4">${__("Not set")}</span>`;
		const days_left = frappe.datetime.get_day_diff(
			row.payment_due_date,
			frappe.datetime.now_date()
		);
		const is_open = row.workflow_state !== "Paid";
		const tone =
			is_open && days_left < 0
				? "text-ink-red-5"
				: is_open && days_left <= 7
				? "text-ink-amber-6"
				: "text-ink-gray-6";
		return `<span class="text-sm ${tone}">${frappe.datetime.str_to_user(
			row.payment_due_date
		)}</span>`;
	}

	get_filters() {
		return { ...nfi.desk.get_filter_values(this.filters), state: this.state };
	}

	set_summary(result) {
		const stats = [
			{ label: __("Cases"), value: String(result.total) },
			{
				label: __("Final sponsor amount"),
				value: nfi.desk.format_money(result.summary.sponsored),
			},
			{ label: __("Total paid"), value: nfi.desk.format_money(result.summary.paid) },
			{ label: __("Balance to pay"), value: nfi.desk.format_money(result.summary.balance) },
		];
		this.summary.find(".nfi-payment-stats").html(
			stats
				.map(
					(stat) => `<div class="col-6 col-md-3 nfi-payment-stat">
						<div class="text-xs text-ink-gray-5">${stat.label}</div>
						<div class="text-2xl-semibold text-ink-gray-9 mt-1">${stat.value}</div>
					</div>`
				)
				.join("")
		);
	}

	async refresh() {
		await this.table.refresh();
	}
}
