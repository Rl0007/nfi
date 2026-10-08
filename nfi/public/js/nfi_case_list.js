frappe.provide("nfi.desk");

nfi.desk.PAGE_LENGTHS = [20, 100, 500];

nfi.desk.STATE_THEMES = {
	Draft: "gray",
	"Information needed": "amber",
	"Coordinator Verification": "blue",
	"Medical Review": "violet",
	"Social & Financial Review": "violet",
	"Director Review": "violet",
	"Coordinator Review": "blue",
	"Approved – Awaiting Final Discharge Documents": "green",
	"Accountant Review": "blue",
	"Payment Processed": "blue",
	"Partially Paid": "amber",
	Paid: "green",
	Rejected: "red",
	Closed: "gray",
};

nfi.desk.PROGRAM_THEMES = { BRP: "blue", BCRP: "violet", BARP: "amber", TBC: "green", SRT: "red" };

nfi.desk.LatestRequest = class LatestRequest {
	constructor() {
		this.request_id = 0;
	}

	start() {
		this.request_id += 1;
		const request_id = this.request_id;
		return () => request_id === this.request_id;
	}
};

nfi.desk.format_state = (state) =>
	frappe.ui.badge.html({ label: __(state), theme: nfi.desk.STATE_THEMES[state] || "gray" });

nfi.desk.format_program = (program) =>
	program
		? frappe.ui.badge.html({
				label: program,
				theme: nfi.desk.PROGRAM_THEMES[program] || "gray",
				variant: "outline",
		  })
		: "";

nfi.desk.format_money = (value) => (flt(value) ? format_currency(value, "INR", 0) : "—");

nfi.desk.format_age = (datetime) => {
	const days = frappe.datetime.get_day_diff(frappe.datetime.now_date(), datetime);
	if (days < 1) return __("Today");
	return days === 1 ? __("1 day") : __("{0} days", [days]);
};

nfi.desk.format_case = (row) => {
	const escape = frappe.utils.escape_html;
	return `<div class="min-w-0">
		<div class="truncate text-base-medium text-ink-gray-8">${escape(row.title || row.name)}</div>
		<div class="truncate text-sm text-ink-gray-5 mt-1">${escape(row.mother_name || "")}</div>
	</div>`;
};

nfi.desk.open_case = (name) => frappe.set_route("Form", "NFI Case", name);

nfi.desk.add_case_filters = (page, on_change) =>
	Object.fromEntries(
		[
			{
				fieldname: "hospital",
				label: __("Hospital"),
				fieldtype: "Link",
				options: "NFI Hospital",
			},
			{
				fieldname: "program",
				label: __("Program"),
				fieldtype: "Link",
				options: "NFI Program",
			},
			{ fieldname: "search", label: __("Case no, baby or parent"), fieldtype: "Data" },
		].map((df) => [df.fieldname, page.add_field({ ...df, change: on_change })])
	);

nfi.desk.get_filter_values = (filters) =>
	Object.fromEntries(
		Object.entries(filters).map(([fieldname, field]) => [fieldname, field.get_value() || null])
	);

nfi.desk.CaseTable = class CaseTable {
	constructor({ method, columns, get_args, on_page, empty_title }) {
		this.method = method;
		this.columns = columns;
		this.get_args = get_args;
		this.on_page = on_page;
		this.empty_title = empty_title;
		this.rows = [];
		this.page_length = nfi.desk.PAGE_LENGTHS[0];
		this.latest_request = new nfi.desk.LatestRequest();
		this.wrapper = $(`<div class="frappe-card shadow-none p-0 overflow-hidden">
			<div class="table-responsive"><table class="table table-hover mt-0 mb-0 nfi-case-table">
				<thead><tr></tr></thead><tbody></tbody>
			</table></div>
		</div>`);
		for (const column of columns) {
			$(`<th class="text-sm text-ink-gray-5"></th>`)
				.text(column.label)
				.toggleClass("text-right", column.align === "right")
				.appendTo(this.wrapper.find("thead tr"));
		}
		this.add_paging_area();
	}

	add_paging_area() {
		this.paging_area = $(`<div class="list-paging-area level px-3 py-3 border-t">
			<div class="level-left"></div><div class="level-right"></div>
		</div>`)
			.hide()
			.appendTo(this.wrapper);
		const sizes = new frappe.ui.TabButtons({
			label: __("Page Size"),
			options: nfi.desk.PAGE_LENGTHS.map((value) => ({ label: String(value), value })),
			value: this.page_length,
			on_change: (value) => {
				this.page_length = value;
				this.refresh();
			},
		});
		this.paging_area.find(".level-left").append(sizes.$el);
		this.paging_area.find(".level-right").append(
			frappe.ui.button({
				label: __("Load More"),
				css_class: "btn-more",
				onclick: () => this.load(this.rows.length),
			})
		);
	}

	async refresh() {
		this.wrapper.find("tbody").empty();
		await this.load(0);
	}

	async load(start) {
		const is_current = this.latest_request.start();
		this.add_skeleton_rows(start ? 3 : 6);
		try {
			const page = await frappe.xcall(this.method, {
				...this.get_args(),
				start,
				page_length: this.page_length,
			});
			if (is_current()) this.add_page(page, start);
		} finally {
			if (is_current()) this.wrapper.find("tbody .list-skeleton-row").remove();
		}
	}

	add_skeleton_rows(count) {
		const body = this.wrapper.find("tbody");
		for (let index = 0; index < count; index++) {
			const row = $(`<tr class="list-skeleton-row"></tr>`).appendTo(body);
			for (const column of this.columns) {
				$("<td></td>")
					.append(frappe.ui.skeleton({ height: column.skeleton_height || "14px" }))
					.appendTo(row);
			}
		}
	}

	add_page(page, start) {
		this.rows = start ? [...this.rows, ...page.rows] : page.rows;
		this.on_page?.(page);
		const body = this.wrapper.find("tbody");
		if (!start) body.empty();
		if (!this.rows.length) {
			$("<td></td>")
				.attr("colspan", this.columns.length)
				.append(frappe.ui.empty_state({ icon: "inbox", title: this.empty_title }))
				.appendTo($("<tr></tr>").appendTo(body));
		}
		for (const row of page.rows) this.add_row(body, row);
		this.paging_area.toggle(page.total > nfi.desk.PAGE_LENGTHS[0]);
		this.paging_area.find(".btn-more").toggle(this.rows.length < page.total);
	}

	add_row(body, row) {
		const table_row = $(`<tr class="cursor-pointer"></tr>`)
			.attr("data-name", row.name)
			.on("click", () => nfi.desk.open_case(row.name))
			.appendTo(body);
		for (const column of this.columns) {
			$(`<td class="align-middle"></td>`)
				.toggleClass("text-right", column.align === "right")
				.html(column.format(row))
				.appendTo(table_row);
		}
	}
};
