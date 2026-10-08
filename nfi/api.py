import frappe
from frappe.query_builder.functions import Max
from frappe.utils import cint, flt

from nfi.install import APPROVED_AWAITING_DOCUMENTS

COORDINATOR_QUEUE_STATES = (
	"Coordinator Verification",
	"Medical Review",
	"Social & Financial Review",
	"Coordinator Review",
	APPROVED_AWAITING_DOCUMENTS,
	"Paid",
)
PIPELINE_STATES = (
	"Coordinator Verification",
	"Information needed",
	"Medical Review",
	"Social & Financial Review",
	"Director Review",
	"Coordinator Review",
	APPROVED_AWAITING_DOCUMENTS,
	"Accountant Review",
	"Payment Processed",
	"Partially Paid",
	"Paid",
)
PAYMENT_STATES = ("Accountant Review", "Payment Processed", "Partially Paid", "Paid")
PIPELINE_CARDS_PER_STAGE = 50
CASE_FIELDS = [
	"name",
	"case_number",
	"baby_name",
	"mother_name",
	"hospital",
	"program",
	"workflow_state",
	"modified",
]


@frappe.whitelist()
def get_case_queue(
	hospital: str | None = None,
	program: str | None = None,
	search: str | None = None,
	start: int = 0,
	page_length: int = 20,
) -> dict:
	query = get_case_query(COORDINATOR_QUEUE_STATES, hospital, program, search)
	rows = frappe.get_list(
		**query,
		fields=[*CASE_FIELDS, "recommended_amount", "director_approved_amount"],
		order_by="modified asc",
		start=max(cint(start), 0),
		page_length=max(cint(page_length), 1),
	)
	add_stage_since(rows)
	return {"rows": rows, "total": get_case_count(query)}


@frappe.whitelist()
def get_case_pipeline(
	hospital: str | None = None, program: str | None = None, search: str | None = None
) -> list[dict]:
	query = get_case_query(PIPELINE_STATES, hospital, program, search)
	counts = {
		row.workflow_state: row.total
		for row in frappe.get_list(
			**query,
			fields=["workflow_state", {"COUNT": "*", "as": "total"}],
			group_by="workflow_state",
			order_by=None,
		)
	}
	stages = []
	for state in PIPELINE_STATES:
		rows = frappe.get_list(
			doctype="NFI Case",
			filters={**query["filters"], "workflow_state": state},
			or_filters=query.get("or_filters"),
			fields=[*CASE_FIELDS, "recommended_amount", "director_approved_amount", "final_sponsor_amount"],
			order_by="modified asc",
			page_length=PIPELINE_CARDS_PER_STAGE,
		)
		add_stage_since(rows)
		stages.append({"state": state, "total": counts.get(state, 0), "rows": rows})
	return stages


@frappe.whitelist()
def get_payment_list(
	state: str | None = None,
	hospital: str | None = None,
	program: str | None = None,
	search: str | None = None,
	start: int = 0,
	page_length: int = 20,
) -> dict:
	if state and state not in PAYMENT_STATES:
		frappe.throw(frappe._("Unknown payment status {0}").format(state))
	query = get_case_query(PAYMENT_STATES, hospital, program, search)
	if state:
		query["filters"]["workflow_state"] = state
	rows = frappe.get_list(
		**query,
		fields=[*CASE_FIELDS, "final_sponsor_amount", "total_paid", "payment_due_date"],
		order_by="payment_due_date asc, modified asc",
		start=max(cint(start), 0),
		page_length=max(cint(page_length), 1),
	)
	for row in rows:
		row.balance = flt(row.final_sponsor_amount) - flt(row.total_paid)
	return {"rows": rows, "total": get_case_count(query), "summary": get_payment_summary(query)}


def get_case_query(
	states: tuple[str, ...], hospital: str | None, program: str | None, search: str | None
) -> dict:
	filters = {"workflow_state": ["in", states]}
	if hospital:
		filters["hospital"] = hospital
	if program:
		filters["program"] = program
	query = {"doctype": "NFI Case", "filters": filters}
	if search and search.strip():
		pattern = f"%{search.strip()}%"
		query["or_filters"] = [
			["case_number", "like", pattern],
			["baby_name", "like", pattern],
			["mother_name", "like", pattern],
			["father_name", "like", pattern],
		]
	return query


def get_case_count(query: dict) -> int:
	result = frappe.get_list(**query, fields=[{"COUNT": "*", "as": "total"}], order_by=None)
	return cint(result[0].total) if result else 0


def get_payment_summary(query: dict) -> dict:
	result = frappe.get_list(
		**query,
		fields=[
			{"SUM": "final_sponsor_amount", "as": "sponsored"},
			{"SUM": "total_paid", "as": "paid"},
		],
		order_by=None,
	)
	summary = result[0] if result else frappe._dict()
	sponsored, paid = flt(summary.get("sponsored")), flt(summary.get("paid"))
	return {"sponsored": sponsored, "paid": paid, "balance": sponsored - paid}


def add_stage_since(rows: list[dict]) -> None:
	"""Pass-through states are set with db_set and leave no Workflow comment, so `modified` is the fallback."""
	if not rows:
		return
	comment = frappe.qb.DocType("Comment")
	stage_since = dict(
		frappe.qb.from_(comment)
		.select(comment.reference_name, Max(comment.creation))
		.where(
			(comment.reference_doctype == "NFI Case")
			& (comment.comment_type == "Workflow")
			& comment.reference_name.isin([row.name for row in rows])
		)
		.groupby(comment.reference_name)
		.run()
	)
	for row in rows:
		row.stage_since = stage_since.get(row.name) or row.modified
