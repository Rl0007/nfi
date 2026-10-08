import random
from collections import Counter
from datetime import timedelta

import frappe
from frappe.model.workflow import apply_workflow
from frappe.utils import add_days, getdate, now_datetime, today
from frappe.utils.password import update_password

from nfi.demo_files import get_pdf_content, get_png_content
from nfi.install import ACCOUNTANT, ADMIN, COORDINATOR, DIRECTOR, SPOC

PASSWORD = "admin"
COORDINATOR_USER = "coordinator@nfi.demo"
ACCOUNTANT_USER = "accountant@nfi.demo"
USERS = [
	("spoc.sanjeevini@nfi.demo", "Deepa", "Shetty", SPOC),
	("spoc.kaveri@nfi.demo", "Ravi", "Gowda", SPOC),
	(COORDINATOR_USER, "Kavya", "Hegde", COORDINATOR),
	("director.meera@nfi.demo", "Meera", "Raghunath", DIRECTOR),
	("director.arvind@nfi.demo", "Arvind", "Kulkarni", DIRECTOR),
	(ACCOUNTANT_USER, "Suresh", "Nayak", ACCOUNTANT),
	("admin@nfi.demo", "Ananya", "Rao", ADMIN),
]
MEERA = "director.meera@nfi.demo"
ARVIND = "director.arvind@nfi.demo"

HOSPITALS = {
	"SAN": {
		"hospital_name": "Sanjeevini Mother & Child Hospital",
		"city": "Bengaluru (Jayanagar)",
		"nicu_beds": 32,
		"mou_days": 410,
		"spocs": ["spoc.sanjeevini@nfi.demo"],
		"programs": {"BRP": MEERA, "BCRP": MEERA, "BARP": ARVIND, "TBC": ARVIND, "SRT": ARVIND},
		"doctor": "Dr. Prakash Bhat",
	},
	"NAN": {
		"hospital_name": "Nandi Women & Children Hospital",
		"city": "Bengaluru (Yelahanka)",
		"nicu_beds": 24,
		"mou_days": 275,
		"spocs": ["spoc.sanjeevini@nfi.demo"],
		"programs": {"BRP": ARVIND, "BCRP": MEERA, "SRT": MEERA, "TBC": MEERA},
		"doctor": "Dr. Shalini Murthy",
	},
	"KAV": {
		"hospital_name": "Kaveri Neonatal Care Centre",
		"city": "Mysuru",
		"nicu_beds": 18,
		"mou_days": 190,
		"spocs": ["spoc.kaveri@nfi.demo"],
		"programs": {"BRP": MEERA, "BCRP": ARVIND, "BARP": ARVIND, "SRT": ARVIND, "TBC": MEERA},
		"doctor": "Dr. Mohan Kumar S",
	},
	"TUN": {
		"hospital_name": "Tunga Shishu Hospital",
		"city": "Shivamogga",
		"nicu_beds": 14,
		"mou_days": 120,
		"spocs": [],
		"programs": {"BRP": ARVIND, "BARP": MEERA, "TBC": ARVIND},
		"doctor": "Dr. Rajeshwari Patil",
	},
	"HOY": {
		"hospital_name": "Hoysala Newborn & NICU Centre",
		"city": "Hassan",
		"nicu_beds": 12,
		"mou_days": 18,
		"spocs": [],
		"programs": {"BRP": MEERA, "BARP": ARVIND, "BCRP": MEERA},
		"doctor": "Dr. Naveen Gowda",
	},
}

PARENTS = [
	("Lakshmi", "Manjunath"),
	("Shwetha", "Prakash"),
	("Pooja", "Santosh"),
	("Asha", "Ramesh"),
	("Rekha", "Nagaraj"),
	("Kavitha", "Mahesh"),
	("Sunitha", "Basavaraj"),
	("Divya", "Kiran"),
	("Nandini", "Harish"),
	("Bhavya", "Raghavendra"),
	("Roopa", "Shivakumar"),
	("Ayesha Banu", "Imran Pasha"),
	("Manjula", "Venkatesh"),
	("Sowmya", "Girish"),
	("Shabana", "Syed Rafiq"),
	("Mary Joseph", "Antony Joseph"),
	("Gowramma", "Chandrappa"),
	("Parvathi", "Siddaraju"),
	("Savitha", "Umesh"),
	("Chaitra", "Lokesh"),
	("Yashoda", "Krishnappa"),
	("Harshitha", "Darshan"),
	("Ramya", "Praveen"),
	("Tejaswini", "Anand"),
	("Shilpa", "Vinay"),
	("Pushpa", "Thimmaiah"),
	("Anitha", "Mallikarjun"),
	("Reshma", "Abdul Khader"),
	("Geetha", "Rangaswamy"),
	("Vidya", "Sunil"),
	("Sangeetha", "Puttaswamy"),
	("Jyothi", "Halesh"),
]
OCCUPATIONS = ("Auto driver", "Daily-wage labourer", "Farmer", "Tailor", "Security guard", "Mason")
MOBILE_PREFIXES = ("98450", "99000", "63600", "70220", "81970", "96860", "77600", "90080")

APPROVE = ("director_approve", "coordinator_approve")
DISCHARGE = (*APPROVE, "discharge")
# (program, hospital, birth status, gender, days ago, steps after creation, top-up of spec index)
SPECS = [
	("BRP", "SAN", "In-born", "Female", 2, (), None),
	("SRT", "KAV", "In-born", "Male", 1, (), None),
	("BCRP", "NAN", "Out-born", "Male", 6, ("submit", "request_info"), None),
	("BRP", "KAV", "In-born", "Female", 9, ("submit", "request_info"), None),
	("TBC", "SAN", "Out-born", "Male", 4, ("submit",), None),
	("BARP", "KAV", "In-born", "Female", 11, ("submit", "request_info", "resubmit"), None),
	("BRP", "NAN", "In-born", "Male", 15, ("submit", "verify", "medical_query"), None),
	("SRT", "SAN", "In-born", "Female", 8, ("submit", "verify"), None),
	("BRP", "KAV", "Out-born", "Male", 21, ("submit", "verify", "medical", "sf_mixed"), None),
	("BRP", "HOY", "In-born", "Female", 18, ("submit", "verify", "medical"), None),
	("BARP", "SAN", "In-born", "Male", 12, ("submit", "verify"), None),
	("TBC", "TUN", "Out-born", "Female", 14, ("submit", "verify", "medical"), None),
	("BCRP", "KAV", "In-born", "Male", 19, ("submit", "verify", "medical"), None),
	("BRP", "NAN", "In-born", "Female", 27, ("to_director", "director_reject"), None),
	("BCRP", "HOY", "Out-born", "Male", 24, ("submit", "verify", "medical_reject"), None),
	("BRP", "SAN", "In-born", "Male", 33, ("to_director", *APPROVE, "upload_discharge"), None),
	("SRT", "NAN", "In-born", "Female", 38, ("to_director", *APPROVE, "upload_discharge"), None),
	("BARP", "TUN", "In-born", "Male", 30, ("to_director", *APPROVE, "upload_discharge"), None),
	("TBC", "KAV", "Out-born", "Female", 44, ("to_director", *DISCHARGE), None),
	("BRP", "TUN", "In-born", "Male", 49, ("to_director", *DISCHARGE, "accountant_return"), None),
	("BCRP", "SAN", "In-born", "Female", 41, ("to_director", *DISCHARGE), None),
	("BRP", "KAV", "In-born", "Male", 55, ("to_director", *DISCHARGE, "process_payment"), None),
	(
		"SRT",
		"SAN",
		"In-born",
		"Male",
		60,
		("to_director", *DISCHARGE, "process_payment", "pay_partial"),
		None,
	),
	(
		"BRP",
		"HOY",
		"Out-born",
		"Female",
		64,
		("to_director", *DISCHARGE, "process_payment", "pay_partial"),
		None,
	),
	("BCRP", "NAN", "In-born", "Male", 68, ("to_director", *DISCHARGE, "process_payment", "pay_full"), None),
	(
		"BARP",
		"KAV",
		"In-born",
		"Female",
		72,
		("to_director", *DISCHARGE, "process_payment", "pay_full"),
		None,
	),
	(
		"BRP",
		"SAN",
		"In-born",
		"Female",
		88,
		(
			"submit",
			"request_info",
			"resubmit",
			"to_director",
			*DISCHARGE,
			"process_payment",
			"pay_partial",
			"pay_full",
			"close",
		),
		None,
	),
	(
		"TBC",
		"NAN",
		"Out-born",
		"Male",
		84,
		("to_director", *DISCHARGE, "process_payment", "pay_full", "close"),
		None,
	),
	(
		"SRT",
		"KAV",
		"In-born",
		"Female",
		79,
		("to_director", *DISCHARGE, "process_payment", "pay_full", "close"),
		None,
	),
	("BRP", "TUN", "Out-born", "Male", 35, ("submit", "verification_reject"), None),
	("BARP", "SAN", "In-born", "Female", 46, ("to_director", "director_reject", "coordinator_reject"), None),
	(
		"BRP",
		"NAN",
		"In-born",
		"Male",
		52,
		("submit", "verify", "medical", "sf_reject", "coordinator_reject"),
		None,
	),
	("BRP", "SAN", "In-born", "Female", 10, ("to_director",), 26),
	("SRT", "NAN", "In-born", "Female", 5, ("submit",), 16),
]


def make():
	frappe.set_user("Administrator")  # nosemgrep
	add_users()
	add_hospitals()
	cases = {}
	for index in sorted(range(len(SPECS)), key=lambda index: -SPECS[index][4]):
		cases[index] = DemoCase(index, SPECS[index], cases).make()
	frappe.set_user("Administrator")  # nosemgrep
	print(get_summary())


def clear():
	frappe.set_user("Administrator")  # nosemgrep
	mobiles = [get_mobile(index, 0) for index in range(len(SPECS))]
	for case_name in frappe.get_all(
		"NFI Case", filters={"mother_mobile": ("in", mobiles)}, order_by="is_topup desc", pluck="name"
	):
		frappe.delete_doc("NFI Case", case_name, force=True, ignore_permissions=True)
	if not frappe.db.count("NFI Case"):
		for prefix in ("NFI-", "TP-"):
			frappe.db.delete("Series", {"name": ("like", f"{prefix}%")})
	for hospital in HOSPITALS.values():
		frappe.delete_doc_if_exists("NFI Hospital", hospital["hospital_name"], force=True)
	for email, *_ in USERS:
		frappe.delete_doc_if_exists("User", email, force=True)


def get_summary() -> dict:
	return {
		"by_state": Counter(frappe.get_all("NFI Case", pluck="workflow_state")),
		"by_program": Counter(frappe.get_all("NFI Case", pluck="program")),
		"cases": frappe.db.count("NFI Case"),
		"files": frappe.db.count("File", {"attached_to_doctype": "NFI Case"}),
	}


def add_users():
	for email, first_name, last_name, role in USERS:
		if frappe.db.exists("User", email):
			continue
		user = frappe.new_doc("User")
		user.update(
			{
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"send_welcome_email": 0,
			}
		)
		user.append("roles", {"role": role})
		user.insert()
		update_password(email, PASSWORD)


def add_hospitals():
	for hospital in HOSPITALS.values():
		if frappe.db.exists("NFI Hospital", hospital["hospital_name"]):
			continue
		doc = frappe.new_doc("NFI Hospital")
		doc.update(
			{
				"hospital_name": hospital["hospital_name"],
				"city": hospital["city"],
				"nicu_beds": hospital["nicu_beds"],
				"mou_expiry_date": add_days(today(), hospital["mou_days"]),
				"spocs": [{"user": user} for user in hospital["spocs"]],
				"programs": [
					{"program": program, "director": director}
					for program, director in hospital["programs"].items()
				],
			}
		)
		doc.insert()
		mou = save_file(
			"NFI Hospital",
			doc.name,
			"mou.pdf",
			get_pdf_content(["Memorandum of Understanding", doc.name, "Neonatal Foundation of India"]),
		)
		doc.db_set("mou_file", mou)


def save_file(doctype: str, name: str, file_name: str, content: bytes) -> str:
	file = frappe.new_doc("File")
	file.update(
		{
			"file_name": file_name,
			"content": content,
			"attached_to_doctype": doctype,
			"attached_to_name": name,
			"is_private": 1,
		}
	)
	file.insert()
	return file.file_url


def get_mobile(index: int, offset: int) -> str:
	return f"{MOBILE_PREFIXES[(index + offset) % len(MOBILE_PREFIXES)]}{(index * 7919 + offset * 104729) % 100000:05d}"


class DemoCase:
	def __init__(self, index: int, spec: tuple, cases: dict):
		self.program, hospital_key, self.birth_status, self.gender, days_ago, self.steps, topup_of = spec
		self.hospital = HOSPITALS[hospital_key]
		self.original = cases.get(topup_of)
		self.parent_index = index if topup_of is None else topup_of
		self.rng = random.Random(index)
		self.mother, self.father = PARENTS[self.parent_index]
		self.started_on = now_datetime() - timedelta(days=days_ago, hours=self.rng.randint(1, 8))
		self.clock = self.started_on
		self.step_gap = timedelta(hours=days_ago * 24 / (len(self.steps) + 2))
		self.estimate = self.rng.randrange(150, 300 if self.program == "SRT" else 600) * 1000
		self.vials = self.rng.randint(1, 2) if self.program == "SRT" else 0
		self.name = None

	@property
	def spoc(self) -> str:
		return self.hospital["spocs"][0] if self.hospital["spocs"] else COORDINATOR_USER

	@property
	def case_type(self) -> str:
		return "Top-up" if self.original else "Fresh Case"

	def make(self) -> str:
		mother_mobile = get_mobile(self.parent_index, 0)
		self.name = frappe.db.get_value(
			"NFI Case", {"mother_mobile": mother_mobile, "case_type": self.case_type}
		)
		if self.name:
			if "upload_discharge" in self.steps:
				self.upload_discharge()
			return self.name
		self.add_case(mother_mobile)
		for step in self.steps:
			self.clock += self.step_gap
			getattr(self, step)()
		frappe.set_user("Administrator")  # nosemgrep
		frappe.db.set_value(
			"NFI Case",
			self.name,
			{"creation": self.started_on, "modified": min(self.clock, now_datetime())},
			update_modified=False,
		)
		return self.name

	def add_case(self, mother_mobile: str):
		frappe.set_user(self.spoc)  # nosemgrep
		case = frappe.new_doc("NFI Case")
		case.update(
			{
				"case_type": self.case_type,
				"original_case": self.original,
				"hospital": self.hospital["hospital_name"],
				"program": self.program,
				"mother_name": self.mother,
				"mother_mobile": mother_mobile,
				"father_name": self.father,
				"father_mobile": get_mobile(self.parent_index, 3),
				"gender": self.gender,
				"birth_status": self.birth_status,
			}
		)
		case.insert()
		self.name = case.name
		self.update(self.spoc, lambda case: self.upload_documents(case, "Intake"))

	def update(self, user: str, change, action: str | None = None):
		frappe.set_user(user)  # nosemgrep
		case = frappe.get_doc("NFI Case", self.name)
		if callable(change):
			change(case)
		elif change:
			case.update(change)
		if change:
			case.save()
		if action:
			apply_workflow(case, action)

	def upload_documents(self, case, stage: str):
		for row in case.documents:
			if row.stage != stage or row.file:
				continue
			if not (row.is_mandatory or row.document_type in ("Father Aadhaar Card", "Mother Aadhaar Card")):
				continue
			slug = frappe.scrub(row.document_type).replace("_", "-")
			if "Photo" in row.document_type or "Video" in row.document_type:
				content = get_png_content((self.rng.randint(150, 230), 200, self.rng.randint(170, 240)))
				file_name = f"{slug}.png"
			else:
				lines = [row.document_type, case.baby_name, case.hospital, case.case_number or "Draft"]
				content = get_pdf_content(lines)
				file_name = f"{slug}.pdf"
			row.file = save_file("NFI Case", case.name, file_name, content)

	def add_log(self, case, committee: str, entry_type: str, message: str):
		case.append(
			"review_log",
			{
				"committee": committee,
				"entry_type": entry_type,
				"message": message,
				"logged_on": self.clock,
				"logged_by": frappe.session.user,
			},
		)

	def get_recommended_amount(self) -> int:
		if self.program == "TBC":
			return 50000
		if self.program == "SRT":
			return self.vials * 18500
		share = {"BRP": 0.5, "BCRP": 0.35, "BARP": 0.3}[self.program]
		return round(self.estimate * share / 5000) * 5000

	def submit(self):
		self.update(self.spoc, None, "Submit")

	def request_info(self):
		reason = self.rng.choice(
			[
				"Interim summary is missing the doctor's signature and hospital stamp. Please re-upload.",
				"Mother's Aadhaar is not readable. Please upload a clear scan of both sides.",
				"Fund Application Form page 3 (income details) is blank. Please get it filled by the father.",
			]
		)
		self.update(COORDINATOR_USER, {"return_reason": reason}, "Request Information")

	def resubmit(self):
		self.update(self.spoc, None, "Resubmit")

	def to_director(self):
		if "submit" not in self.steps:
			self.submit()
		self.verify()
		if self.get_route() != "Director Only":
			self.medical()
		if self.get_route() == "Medical, Social & Financial":
			self.social_financial()

	def get_route(self) -> str:
		return frappe.db.get_value("NFI Program", self.program, "review_route")

	def verify(self):
		self.update(COORDINATOR_USER, self.set_case_details)
		if self.get_route() == "Director Only":
			amount = {"recommended_amount": self.get_recommended_amount()}
			self.update(COORDINATOR_USER, amount, "Send to Director")
		else:
			self.update(COORDINATOR_USER, {"medical_status": "Pending"}, "Send to Medical Review")

	def set_case_details(self, case):
		case.update(get_case_details(self))
		case.hospital_estimate = self.estimate
		if self.original:
			case.requested_topup = round(self.estimate * 0.25 / 5000) * 5000
		if self.rng.random() < 0.4:
			case.append(
				"bene_calls",
				{
					"call_date": self.clock - timedelta(hours=26),
					"outcome": "Not Reachable",
					"notes": "Father's phone switched off. Will retry tomorrow.",
				},
			)
		case.append(
			"bene_calls",
			{
				"call_date": self.clock,
				"outcome": "Reached - Verified",
				"notes": (
					f"Spoke to {self.father} in Kannada. Confirmed NICU admission, monthly income and that "
					"no other trust or insurance is covering the bill. Family has paid an advance by "
					"borrowing from relatives."
				),
			},
		)

	def medical_query(self):
		def change(case):
			case.medical_status = "Query Raised"
			self.add_log(case, "Medical", "Query", "Please share the latest chest X-ray and CRP trend.")
			self.add_log(
				case, "Medical", "Response", "Hospital shared X-ray dated today; CRP down to 6 mg/L."
			)

		self.update(COORDINATOR_USER, change)

	def medical(self):
		def change(case):
			case.medical_status = "Approved"
			self.add_log(
				case, "Medical", "Decision", "Clinically eligible. Prognosis good with continued NICU care."
			)
			if self.get_route() == "Medical":
				case.recommended_amount = self.get_recommended_amount()
				case.srt_vials = self.vials
			else:
				case.social_status = case.financial_status = "Pending"

		action = "Send to Director" if self.get_route() == "Medical" else "Send to Social & Financial Review"
		self.update(COORDINATOR_USER, change, action)

	def medical_reject(self):
		def change(case):
			case.medical_status = "Rejected"
			self.add_log(
				case,
				"Medical",
				"Decision",
				"Congenital anomaly with poor prognosis; outside programme criteria.",
			)

		self.update(COORDINATOR_USER, change, "Send to Coordinator Review")

	def sf_mixed(self):
		def change(case):
			case.social_status = "Approved"
			case.financial_status = "Query Raised"
			self.add_log(case, "Social", "Decision", "Home visit done; family situation genuine.")
			self.add_log(case, "Financial", "Query", "Bank statement shows a ₹60,000 credit in May. Source?")

		self.update(COORDINATOR_USER, change)

	def social_financial(self):
		def change(case):
			case.social_status = case.financial_status = "Approved"
			case.recommended_amount = self.get_recommended_amount()
			self.add_log(case, "Social", "Decision", "Approved. First child after 6 years of marriage.")
			self.add_log(
				case, "Financial", "Decision", "Approved. Income below ₹20,000 per month, no assets."
			)

		self.update(COORDINATOR_USER, change, "Send to Director")

	def sf_reject(self):
		def change(case):
			case.social_status = "Approved"
			case.financial_status = "Rejected"
			self.add_log(
				case,
				"Financial",
				"Decision",
				"Family owns 4 acres of irrigated land; not eligible for support.",
			)

		self.update(COORDINATOR_USER, change, "Send to Coordinator Review")

	def director_approve(self):
		def change(case):
			amount = case.recommended_amount
			if self.original:
				case.approved_topup = case.requested_topup
			trimmed = self.program in ("BRP", "BCRP", "BARP") and self.rng.random() < 0.3
			case.director_approved_amount = amount - 5000 if trimmed else amount
			self.add_log(case, "Director", "Decision", "Approved as recommended by the committee.")

		self.update(self.get_director(), change, "Approve")

	def director_reject(self):
		def change(case):
			self.add_log(
				case, "Director", "Decision", "Not approved: hospital bill largely covered by PMJAY."
			)

		self.update(self.get_director(), change, "Reject")

	def get_director(self) -> str:
		return frappe.db.get_value("NFI Case", self.name, "director")

	def coordinator_approve(self):
		self.update(COORDINATOR_USER, None, "Approve")

	def coordinator_reject(self):
		reason = "Not eligible after committee review. Family informed by phone; hospital informed by email."
		self.update(COORDINATOR_USER, {"rejection_reason": reason}, "Reject")

	def verification_reject(self):
		reason = "Baby already discharged before application; NFI supports only ongoing NICU admissions."
		self.update(COORDINATOR_USER, {"rejection_reason": reason}, "Reject")

	def upload_discharge(self):
		self.update(self.spoc, lambda case: self.upload_documents(case, "Discharge"))

	def discharge(self):
		self.upload_discharge()
		discharged_on = getdate(self.clock - timedelta(days=2))
		self.update(
			COORDINATOR_USER,
			{"discharge_or_death_date": discharged_on, "final_bill": round(self.estimate * 1.1, -3)},
			"Send to Accountant",
		)

	def accountant_return(self):
		reason = (
			"Final bill does not show the NFI sponsor amount as a deduction. Ask the hospital to reissue."
		)
		self.update(ACCOUNTANT_USER, {"return_reason": reason}, "Return to Coordinator")

	def process_payment(self):
		def change(case):
			case.final_sponsor_amount = case.director_approved_amount
			case.payment_due_date = getdate(self.clock + timedelta(days=15))
			if self.steps[-1] == "close" and self.program == "TBC":
				case.mortality = 1
				case.mortality_date = case.discharge_or_death_date

		self.update(ACCOUNTANT_USER, change, "Process Payment")

	def pay_partial(self):
		self.update(ACCOUNTANT_USER, lambda case: self.add_payment(case, 0.6))

	def pay_full(self):
		self.update(ACCOUNTANT_USER, lambda case: self.add_payment(case, 1))

	def add_payment(self, case, share: float):
		amount = round(case.final_sponsor_amount * share - case.total_paid)
		case.append(
			"payments",
			{
				"payment_date": getdate(self.clock),
				"amount": amount,
				"mode": self.rng.choice(("NEFT", "RTGS", "IMPS")),
				"reference": f"UTR{self.rng.randint(10**11, 10**12 - 1)}",
			},
		)

	def close(self):
		values = {"post_discharge_photo_status": "Received", "video_testimonial_status": "Received"}
		self.update(COORDINATOR_USER, values, "Close")


def get_case_details(demo: DemoCase) -> dict:
	rng = demo.rng
	hospital = demo.hospital
	cooled = demo.program == "TBC"
	weight = rng.randint(2600, 3400) if cooled else rng.randint(850, 2100)
	weeks = rng.randint(37, 40) if cooled else rng.randint(27, 34)
	born_on = getdate(demo.started_on - timedelta(days=rng.randint(3, 12)))
	wages = rng.randrange(8, 22) * 1000
	occupation = rng.choice(OCCUPATIONS)
	address = f"#{rng.randint(10, 400)}, {rng.choice(['2nd Cross', 'Main Road', 'Temple Street'])}, {hospital['city']}"
	out_born = demo.birth_status == "Out-born"
	diagnosis = "checked"
	return {
		"fa_baby_or_beneficiary_name": f"B/O {demo.mother}",
		"fa_baby_date_of_birth": born_on.strftime("%d-%m-%Y"),
		"fa_time_of_birth": f"{rng.randint(1, 12):02d}:{rng.randint(0, 59):02d} {rng.choice(['AM', 'PM'])}",
		"fa_gender": demo.gender,
		"fa_birth_weight": f"{weight / 1000:.2f} kg",
		"fa_gestational_age": f"{weeks} weeks {rng.randint(0, 6)} days",
		"fa_inborn_or_outborn": demo.birth_status,
		"fa_outborn_hospital_name": "Taluk General Hospital" if out_born else "",
		"fa_nicu_admission_date": born_on.strftime("%d-%m-%Y"),
		"fa_estimated_nicu_stay": f"{rng.randint(2, 6)} weeks",
		"fa_type_of_delivery": rng.choice(["LSCS", "Normal vaginal delivery"]),
		"fa_type_of_conception": rng.choice(["Natural", "Natural", "IUI"]),
		"fa_gravida": f"G{rng.randint(1, 3)}P{rng.randint(0, 1)}",
		"fa_mother_name": demo.mother,
		"fa_mother_occupation": "Homemaker",
		"fa_mother_education": rng.choice(["SSLC", "PUC", "B.Com"]),
		"fa_mother_address": address,
		"fa_father_name": demo.father,
		"fa_father_occupation": occupation,
		"fa_father_education": rng.choice(["7th standard", "SSLC", "ITI"]),
		"fa_father_address": address,
		"fa_father_monthly_or_daily_wages": f"₹{wages:,} per month",
		"fa_father_assets_land_or_house": rng.choice(
			["Rented house, no land", "Own house (kutcha), no land"]
		),
		"fa_number_of_family_members": rng.randint(3, 7),
		"fa_total_estimated_hospital_bill": f"₹{demo.estimate:,}",
		"fa_advance_paid_by_family": f"₹{rng.randrange(10, 60) * 1000:,}",
		"fa_current_outstanding_bill": f"₹{round(demo.estimate * 0.4, -3):,.0f}",
		"fa_other_support_received": "unchecked",
		"fa_doctor_name": hospital["doctor"],
		"fa_designation": "Consultant Neonatologist",
		"fa_doctor_signoff_complete": "checked",
		"fa_signature_present": "checked",
		"fa_stamp_present": "checked",
		"fa_parent_signature_present": "checked",
		"fa_tahsildar_income_certificate": rng.choice(["checked", "not present"]),
		"fa_bank_statement_last_six_months": rng.choice(["checked", "unchecked"]),
		"fa_information_truth_declaration_present": "checked",
		"interim_name": f"B/O {demo.mother}",
		"interim_date_of_birth": born_on.strftime("%d-%m-%Y"),
		"interim_gender": demo.gender,
		"interim_birth_weight_grams": weight,
		"interim_today_s_weight_grams": weight + rng.randint(-120, 180),
		"interim_gestational_age": f"{weeks}+{rng.randint(0, 6)} weeks",
		"interim_apgar_score": f"{rng.randint(2, 4) if cooled else rng.randint(5, 7)}/1 min, "
		f"{rng.randint(4, 6) if cooled else rng.randint(7, 9)}/5 min",
		"interim_place_of_birth": "Taluk General Hospital" if out_born else hospital["hospital_name"],
		"interim_inborn": "unchecked" if out_born else "checked",
		"interim_outborn": "checked" if out_born else "unchecked",
		"interim_age_years": rng.randint(20, 34),
		"interim_married_life_years": rng.randint(1, 8),
		"interim_gravida": rng.randint(1, 3),
		"interim_para": rng.randint(0, 2),
		"interim_living_children": rng.randint(0, 1),
		"interim_natural_conception": "checked",
		"interim_antenatal_risk_factors": rng.choice(
			["Pregnancy-induced hypertension", "Gestational diabetes", "PPROM > 18 hours", "None"]
		),
		"interim_diagnosis_prematurity": "unchecked" if cooled else diagnosis,
		"interim_diagnosis_low_birth_weight": "unchecked" if cooled else diagnosis,
		"interim_diagnosis_respiratory_distress_syndrome": "checked"
		if demo.program == "SRT"
		else "unchecked",
		"interim_diagnosis_sepsis": rng.choice(["checked", "unchecked"]),
		"interim_diagnosis_neonatal_hyperbilirubinemia": rng.choice(["checked", "unchecked"]),
		"interim_diagnosis_others": "Perinatal asphyxia with HIE stage II" if cooled else "",
		"interim_cpap": "checked",
		"interim_day_of_life": str(rng.randint(3, 15)),
		"interim_ongoing_treatment_respiration_cpap": "checked",
		"interim_ongoing_treatment_feeding_orogastric_feeding": "checked",
		"interim_case_summary": (
			f"{weeks}-week {demo.gender.lower()} baby, {weight} g, admitted on day 1 with respiratory distress. "
			+ ("Therapeutic hypothermia for 72 hours." if cooled else "On CPAP, IV antibiotics, OG feeds.")
		),
		"interim_plan_of_discharge": "Room air, full oral feeds and steady weight gain for 3 days.",
		"interim_signing_doctor_name": hospital["doctor"],
		"interim_signature_present": "checked",
		"interim_stamp_present": "checked",
	}
