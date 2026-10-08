/* global root_element */
const bar_list = root_element.querySelector(".bar-list");
bar_list.querySelector(".bar-list-title").textContent = __(bar_list.dataset.title);

const refresh_bar_list = async () => {
	const data = await frappe.xcall("frappe.desk.doctype.dashboard_chart.dashboard_chart.get", {
		chart_name: bar_list.dataset.chart,
		refresh: 1,
	});
	const labels = data?.labels || [];
	const values = data?.datasets?.[0]?.values || [];
	const largest = Math.max(...values, 1);
	bar_list.querySelector(".bar-list-rows").innerHTML =
		labels
			.map(
				(label, index) => `
			<span class="bar-list-label">${frappe.utils.escape_html(__(label))}</span>
			<span class="bar-list-track">
				<span class="bar-list-fill" style="width: ${(values[index] / largest) * 100}%"></span>
			</span>
			<span class="bar-list-value">${format_number(values[index], null, 0)}</span>`
			)
			.join("") || `<span class="bar-list-empty">${__("Nothing to show yet")}</span>`;
};

refresh_bar_list();
