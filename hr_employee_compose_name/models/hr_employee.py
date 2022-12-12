from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EmployeeNickname(models.Model):
    _inherit = "hr.employee"

    @api.onchange("title", "family_name", "given_names", "local_name")
    def _compute_name(self):
        for employee in self:
            employee.name = employee.compose_name()

    def compose_name(self):
        self.ensure_one()
        if (
            self.country_id.code == "TH"
            and self.company_id.country_id.code == "TH"
            and self.local_name
        ):
            return f"{self.title_th()} {self.local_name}"
        else:
            name = ""
            if self.title:
                name += self.title + " "
            if self.given_names:
                name += self.given_names + " "
            if self.family_name:
                name += self.family_name + " "
            return name.strip()

    def title_th(self):
        if self.title == "Mr":
            return "นาย"
        elif self.title == "Mrs":
            return "นาง"
        elif self.title == "Miss":
            return "นางสาว"

    def write(self, vals):
        res = super(EmployeeNickname, self).write(vals)
        if "title" in vals or "family_name" in vals or "given_names" in vals:
            for employee in self:
                vals["name"] = employee.compose_name()
        return res

    def create(self, vals):
        for rec in self:
            if "title" in vals or "family_name" in vals or "given_names" in vals:
                vals["name"] = rec.compose_name()
        _logger.info("vals: %s", vals)
        return super(EmployeeNickname, self).create(vals)


{
    "active": True,
    "image_1920": False,
    "__last_update": False,
    "given_names": "Jean",
    "family_name": "Sodomie",
    "local_name": False,
    "nickname": False,
    "title": "Mr",
    "job_title": False,
    "category_ids": [[6, False, []]],
    "mobile_phone": False,
    "work_phone": "+1 (650) 555-0111 ",
    "work_email": False,
    "company_id": 1,
    "department_id": False,
    "parent_id": False,
    "coach_id": False,
    "address_id": 1,
    "work_location_id": False,
    "departure_reason_id": False,
    "departure_description": "<p><br></p>",
    "departure_date": False,
    "resource_calendar_id": 1,
    "tz": "Asia/Bangkok",
    "address_home_id": False,
    "lang": False,
    "bank_account_id": False,
    "km_home_work": 0,
    "country_id": False,
    "identification_id": False,
    "tin": False,
    "passport_id": False,
    "gender": False,
    "birthday": False,
    "place_of_birth": False,
    "country_of_birth": False,
    "marital": "single",
    "spouse_complete_name": False,
    "spouse_birthdate": False,
    "children": 0,
    "emergency_contact": False,
    "emergency_phone": False,
    "visa_no": False,
    "permit_no": False,
    "visa_expire": False,
    "work_permit_expiration_date": False,
    "has_work_permit": False,
    "certificate": "other",
    "study_field": False,
    "study_school": False,
    "employee_type": "employee",
    "user_id": False,
    "zkt_privilege": "0",
    "pin": False,
    "barcode": False,
    "contract_id": False,
    "job_id": False,
    "registration_number": False,
    "ss_no": False,
    "ss_subscription_date": False,
    "expenses": True,
    "personal_allowance": True,
    "donations": 0,
    "spouse_allowance": False,
    "parents_allowance": 0,
    "children_before_2018": 0,
    "children_since_2018": 0,
    "insurance_premium": 0,
    "provident_fund": 0,
    "housing_loan": 0,
    "provident_fund_retirement_mutual_fund": 0,
    "ssf": 0,
    "worked_before": "UNEMPLOYED",
    "previous_social_security": 0,
    "previous_withholding_tax": 0,
    "previous_revenue": 0,
    "message_follower_ids": [],
    "activity_ids": [],
    "message_ids": [],
}
