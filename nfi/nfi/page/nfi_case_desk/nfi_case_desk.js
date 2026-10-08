frappe.pages["nfi-case-desk"].on_page_load = async (wrapper) => {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Case Desk"),
		single_column: true,
	});
	await frappe.require("/assets/nfi/js/nfi_case_list.js");
	wrapper.case_desk = new CaseDesk(page);
	wrapper.case_desk.refresh();
};

frappe.pages["nfi-case-desk"].on_page_show = (wrapper) => wrapper.case_desk?.refresh();

class CaseDesk {
	constructor(page) {
		this.page = page;
		page.set_primary_action(__("New Case"), () => frappe.new_doc("NFI Case"), "plus");
		this.filters = nfi.desk.add_case_filters(page, () => this.refresh());
		this.queue = new nfi.desk.CaseTable({
			method: "nfi.api.get_case_queue",
			get_args: () => this.get_filters(),
			on_page: (result) => this.set_count(0, __("My Queue"), result.total),
			empty_title: __("Nothing waiting on you"),
			columns: this.get_queue_columns(),
		});
		this.pipeline = new CasePipeline(this);
		this.tabs = new frappe.ui.Tabs({
			tabs: [
				{ label: __("My Queue"), icon: "inbox", content: this.queue.wrapper[0] },
				{ label: __("Pipeline"), icon: "columns-3", content: this.pipeline.wrapper[0] },
			],
		});
		$('<div class="px-3 pt-3 pb-4"></div>').append(this.tabs.$el).appendTo(page.main);
		this.queue.wrapper.addClass("mt-3");
		this.pipeline.wrapper.addClass("mt-3");
	}

	get_queue_columns() {
		const escape = frappe.utils.escape_html;
		return [
			{ label: __("Case"), format: nfi.desk.format_case, skeleton_height: "32px" },
			{ label: __("Hospital"), format: (row) => escape(row.hospital || "") },
			{ label: __("Program"), format: (row) => nfi.desk.format_program(row.program) },
			{ label: __("Status"), format: (row) => nfi.desk.format_state(row.workflow_state) },
			{
				label: __("In Stage"),
				format: (row) =>
					`<span class="text-sm text-ink-gray-6" title="${escape(
						frappe.datetime.str_to_user(row.stage_since)
					)}">${nfi.desk.format_age(row.stage_since)}</span>`,
			},
			{
				label: __("Amount"),
				align: "right",
				format: (row) =>
					nfi.desk.format_money(row.director_approved_amount || row.recommended_amount),
			},
		];
	}

	get_filters() {
		return nfi.desk.get_filter_values(this.filters);
	}

	set_count(index, label, total) {
		this.tabs.tabs[index].button.lastChild.textContent = `${label} (${total})`;
	}

	async refresh() {
		await Promise.all([this.queue.refresh(), this.pipeline.refresh()]);
	}
}

class CasePipeline {
	constructor(owner) {
		this.owner = owner;
		this.latest_request = new nfi.desk.LatestRequest();
		this.wrapper = $(
			`<div class="nfi-board overflow-x-auto pb-2"><div class="flex gap-3"></div></div>`
		);
		this.board = this.wrapper.children().first();
	}

	async refresh() {
		const is_current = this.latest_request.start();
		this.add_skeleton_columns();
		const stages = await frappe.xcall("nfi.api.get_case_pipeline", this.owner.get_filters());
		if (!is_current()) return;
		this.board.empty();
		for (const stage of stages) this.add_column(stage);
		const total = stages.reduce((sum, stage) => sum + stage.total, 0);
		this.owner.set_count(1, __("Pipeline"), total);
	}

	add_skeleton_columns() {
		this.board.empty();
		for (let index = 0; index < 4; index++) {
			const column = this.make_column();
			for (let card = 0; card < 3; card++) {
				column.find(".nfi-board-cards").append(frappe.ui.skeleton({ height: "88px" }));
			}
		}
	}

	make_column() {
		return $(`<div class="nfi-board-column flex flex-col shrink-0 rounded-lg bg-surface-gray-1">
			<div class="flex items-center gap-2 px-3 pt-3 pb-1 nfi-board-heading"></div>
			<div class="nfi-board-cards flex flex-col gap-2 p-2"></div>
		</div>`).appendTo(this.board);
	}

	add_column(stage) {
		const column = this.make_column().attr("data-state", stage.state);
		const theme = nfi.desk.STATE_THEMES[stage.state] || "gray";
		column
			.find(".nfi-board-heading")
			.append(
				$(`<span class="nfi-board-dot rounded-full bg-surface-${theme}-5"></span>`),
				$(`<span class="truncate text-sm-medium text-ink-gray-8"></span>`)
					.text(__(stage.state))
					.attr("title", __(stage.state)),
				$(`<span class="text-sm text-ink-gray-5"></span>`).text(stage.total)
			);
		const cards = column.find(".nfi-board-cards");
		if (!stage.rows.length) {
			cards.append(
				`<div class="text-sm text-ink-gray-4 text-center py-4">${__("No cases")}</div>`
			);
		}
		for (const row of stage.rows) cards.append(this.make_card(row));
		if (stage.total > stage.rows.length) {
			cards.append(
				frappe.ui.button({
					label: __("{0} more in Case list", [stage.total - stage.rows.length]),
					variant: "ghost",
					size: "sm",
					onclick: () =>
						frappe.set_route("List", "NFI Case", { workflow_state: stage.state }),
				})
			);
		}
	}

	make_card(row) {
		const escape = frappe.utils.escape_html;
		const amount =
			row.final_sponsor_amount || row.director_approved_amount || row.recommended_amount;
		return $(`<div class="nfi-board-card cursor-pointer rounded-lg border bg-surface-elevation-1 p-3">
			<div class="truncate text-base-medium text-ink-gray-9">${escape(row.title || row.name)}</div>
			<div class="flex items-center justify-between mt-2">
				${
					amount
						? `<span class="text-base-semibold text-ink-gray-8">${nfi.desk.format_money(
								amount
						  )}</span>`
						: `<span class="text-sm text-ink-gray-4">${__("No amount yet")}</span>`
				}
				${nfi.desk.format_program(row.program)}
			</div>
			<div class="flex items-center justify-between gap-2 mt-2 text-sm text-ink-gray-6">
				<span class="truncate">${escape(row.hospital || "")}</span>
				<span class="shrink-0">${nfi.desk.format_age(row.stage_since)}</span>
			</div>
		</div>`)
			.attr("data-name", row.name)
			.on("click", () => nfi.desk.open_case(row.name));
	}
}
