from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class ThaiEmployee(models.Model):
    """
    Extand the employee model to have all the data to be able to compute the payslips.
    """

    _inherit = "hr.employee"

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
        default=132,
        groups="hr.group_hr_user",
    )
    expenses = fields.Boolean(
        string="Expenses 50% not over THB 100,000",
        default=True,
        groups="hr.group_hr_user",
    )
    personal_allowance = fields.Boolean(
        string="Personal Allowance THB 60,000", default=True, groups="hr.group_hr_user"
    )
    spouse_allowance = fields.Boolean(
        string="Spouse Allowance THB 60,000", default=False, groups="hr.group_hr_user"
    )
    parents_allowance = fields.Integer(
        string="Parents Allowance THB 30,000", default=0, groups="hr.group_hr_user"
    )
    children_before_2018 = fields.Integer(
        string="Children Allowance THB 30,000", default=0, groups="hr.group_hr_user"
    )
    children_since_2018 = fields.Integer(
        string="Children Allowance THB 60,000", default=0, groups="hr.group_hr_user"
    )
    insurance_premium = fields.Monetary(
        string="Insurance premium (Max THB 100,000)",
        default=0,
        groups="hr.group_hr_user",
    )
    provident_fund = fields.Monetary(
        string="Provident fund allowance (Max 10,000)",
        default=0,
        groups="hr.group_hr_user",
    )
    housing_loan = fields.Monetary(
        string="Housing Loan Interests (Max 100,000)",
        default=0,
        groups="hr.group_hr_user",
    )
    provident_fund_retirement_mutual_fund = fields.Monetary(
        string="Provident Fund/Retirement Mutual Fund : RMF (30% of Income Not over 500,000 Baht)",
        default=0,
        groups="hr.group_hr_user",
    )
    ssf = fields.Monetary(
        string="Super Saving Funds: SSF (30% of Income Not over 500,000 Baht)",
        default=0,
        groups="hr.group_hr_user",
    )
    donations = fields.Monetary(
        string="Donations (Not more than 10% of net taxable income before deduction donation)",
        default=0,
        groups="hr.group_hr_user",
    )

    first_year = fields.Boolean(
        string="First Year At The Company",
        help="Was the employee hired this year ?",
        default=True,
        compute="_compute_first_year",
        groups="hr.group_hr_user",
    )
    worked_before = fields.Selection(
        string="Before Joining Employee was",
        selection=[("UNEMPLOYED", "Unemployed"), ("EMPLOYED", "Employed")],
        default="UNEMPLOYED",
        groups="hr.group_hr_user",
    )
    previous_social_security = fields.Monetary(
        string="Previous Social Security", default=0, groups="hr.group_hr_user"
    )
    previous_withholding_tax = fields.Monetary(
        string="Previous Withholding Tax", default=0, groups="hr.group_hr_user"
    )
    previous_revenue = fields.Monetary(
        string="Previous Revenue", default=0, groups="hr.group_hr_user"
    )

    @api.constrains("parents_allowance", "children_before_2018", "children_since_2018")
    def check_int_fields(self):
        for record in self:
            if (
                record.parents_allowance < 0
                or record.parents_allowance > 4
                or not isinstance(record.parents_allowance, int)
            ):
                raise ValidationError(
                    "Parents allowance must be a positive integer between 0 and 4."
                )
            if record.children_before_2018 < 0 or not isinstance(
                record.children_before_2018, int
            ):
                raise ValidationError(
                    "Children before 2018 must be a positive integer."
                )
            if record.children_since_2018 < 0 or not isinstance(
                record.children_since_2018, int
            ):
                raise ValidationError("Children after 2018 must be a positive integer.")

    @api.constrains(
        "insurance_premium",
        "provident_fund",
        "housing_loan",
        "provident_fund_retirement_mutual_fund",
        "ssf",
        "donations",
    )
    def check_float_fields(self):
        for record in self:
            if record.insurance_premium < 0 or type(record.insurance_premium) not in [
                int,
                float,
            ]:
                raise ValidationError("Insurance Premium must be a positive float.")
            if record.provident_fund < 0 or type(record.provident_fund) not in [
                int,
                float,
            ]:
                raise ValidationError("Provident Fund must be a positive float.")
            if record.housing_loan < 0 or type(record.housing_loan) not in [int, float]:
                raise ValidationError("Housing Loan must be a positive float.")
            if record.provident_fund_retirement_mutual_fund < 0 or type(
                record.provident_fund_retirement_mutual_fund
            ) not in [int, float]:
                raise ValidationError(
                    "Provident Fund Retirement Mutual Fund must be a positive float."
                )
            if record.ssf < 0 or type(record.ssf) not in [int, float]:
                raise ValidationError("SSF must be a positive float.")
            if record.donations < 0 or type(record.donations) not in [int, float]:
                raise ValidationError("Donations must be a positive float.")

    @api.constrains("contract_id")
    def _compute_first_year(self):
        for record in self:
            record.first_year = (
                record.contract_id.date_start.year == datetime.today().year
                if record.contract_id
                else False
            )
