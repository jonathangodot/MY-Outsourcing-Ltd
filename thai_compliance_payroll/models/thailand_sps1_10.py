from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ..utils.const import MONTHS
from ...thai_compliance.utils.const import *
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ThailandSPS1_10(models.Model):
    _name = "thailand.sps1.10"
    _inherit = "thailand.compliance.payroll.common"
    _description = "SPS1_10"
    _order = "year desc"

    account_nb = fields.Char(string="Account Number")
    phone_nb = fields.Char(string="Phone Number", related="company_id.phone")
    fax_nb = fields.Char(
        string="Fax",
        help="Fax ? It's 2022...",
        related="company_id.fax",
    )
    month = fields.Selection(
        MONTHS,
        string="Month",
        required=True,
        default=str(datetime.now().month),
    )
    year = fields.Char(
        string="Year",
        default=datetime.now().year,
        required=True,
    )

    no = fields.Integer(string="No.", default=1)
    total_wages = fields.Monetary(
        string="1. Total wages", compute="_compute_total_wages", store=True
    )
    employee_contrib = fields.Monetary(
        string="2. Employee Contribution",
        compute="_compute_employee_contrib",
        store=True,
    )
    employer_contrib = fields.Monetary(
        string="3. Employer Contribution",
        compute="_compute_employer_contrib",
        store=True,
    )
    total_contrib = fields.Monetary(
        string="4. The total amount of contributions contributed",
        compute="_compute_total_contrib",
        store=True,
    )
    number_of_insured = fields.Integer(
        string="5. The number of the insured who submitted contributions",
        compute="_compute_number_of_insured",
        store=True,
    )

    branch_report = fields.One2many(
        "thailand.sps1.10.branch.report", "sps1_10_id", string="Line"
    )
    company_report = fields.Many2one(
        "thailand.sps1.10.company", string="Company Report"
    )

    @api.constrains("account_nb")
    def _check_account_nb(self):
        """Check format of account nb"""
        for record in self:
            if record.account_nb and len(record.account_nb) != 10:
                raise ValidationError(_("Account Number must be 10 digits long."))

    def format_account_nb(self):
        """Format the account number to fit the PDF form."""
        self.ensure_one()
        if self.account_nb:
            return f"{self.account_nb[0:2]} {self.account_nb[2:9]} {self.account_nb[9]}"

    def _serialize(self, page_size, nb_pages=1):
        """Serialize the data formated for PDF form."""
        self.ensure_one()
        serialized = self.serialize()
        serialized.update(
            {
                "account_nb": self.format_account_nb(),
                "company_fax": self.fax_nb,
                "remittence_month": self.month,
                "remittence_year": self.year_be,
                "total_wages": self.total_wages,
                "employee_contrib": self.employee_contrib,
                "employer_contrib": self.employer_contrib,
                "total_contrib": self.total_contrib,
                "nb_persons": self.number_of_insured,
                "branch_name": self.company_id.name,
                "total_nb_sheets": nb_pages,
                "ss_rate": "{}%".format(
                    self.env["ir.config_parameter"].sudo().get_param("ss_rate")
                ),
                "following_doc_sheet": "✓",
                "following_doc_electronic": "",
                "following_doc_internet": "",
                "other": "",
            }
        )
        employees_groups = [
            self.branch_report[x : x + page_size]
            for x in range(0, len(self.branch_report), page_size)
        ]
        i, p = 1, 1
        for group in employees_groups:
            serialized.update({f"sheet_no_{p}": str(p)})
            for employee in group:
                serialized.update(employee._serialize(i, p))
                if f"wage_tot_{p}" in serialized:
                    serialized[f"wage_tot_{p}"] += employee.actual_wages
                else:
                    serialized[f"wage_tot_{p}"] = employee.actual_wages
                if f"baht_contribution_tot_{p}" in serialized:
                    serialized[f"baht_contribution_tot_{p}"] += employee.contribution
                else:
                    serialized[f"baht_contribution_tot_{p}"] = employee.contribution
                i += 1
            p += 1
            i = 1

        serialized.update({"nb_contrib": p - 1})
        serialized = self.format_serialized_float(serialized, decompose=True)
        serialized = self.clean_serialized(serialized)
        return serialized

    @api.depends("branch_report")
    def _compute_total_wages(self):
        """Adds all the wages of the employees to have the total."""
        for rec in self:
            rec.total_wages = sum([line.actual_wages for line in rec.branch_report])

    @api.depends("branch_report")
    def _compute_employee_contrib(self):
        """Adds all the employee contributions to have the total."""
        for rec in self:
            rec.employee_contrib = sum(
                [line.contribution for line in rec.branch_report]
            )

    @api.depends("employee_contrib")
    def _compute_employer_contrib(self):
        """The employer contribution is the same as the employee contribution, but rounded."""
        for rec in self:
            rec.employer_contrib = round(rec.employee_contrib)

    @api.depends("branch_report")
    def _compute_number_of_insured(self):
        """The number of insured is the number of employees."""
        for rec in self:
            rec.number_of_insured = len(rec.branch_report)

    @api.depends("branch_report")
    def _compute_total_contrib(self):
        """The total contribution is the sum of the employee and employer contributions."""
        for rec in self:
            rec.total_contrib = rec.employee_contrib + rec.employer_contrib

    def generate_report(self):
        """Gets all the informations needed to generate the report and build the Odoo model out of it.
        This document concern the company, therefore, only the social security contributions contributed
        among the company are taken into account."""
        for rec in self:
            self.compute_lines(rec)

    def compute_lines(self, rec):
        """Computes the lines of the report employee by employee."""
        self.branch_report.unlink()
        employees = self.env["hr.employee"].search(
            [
                ("company_id", "=", rec.company_id.id),
            ]
        )
        for employee in employees:
            self.compute_line(rec, employee)

    def compute_line(self, rec, employee):
        """Computes a line of the report for a given employee."""
        if len(self.fetch_contracts(employee, rec)) > 0:
            self.env["thailand.sps1.10.branch.report"].create(
                {
                    "sps1_10_id": rec.id,
                    "employee_id": employee.id,
                    "actual_wages": rec.count_payslip_line(
                        employee, "code_gross", False
                    ),
                    "contribution": -rec.count_payslip_line(
                        employee, "code_secu", False
                    ),
                }
            )

    def pdf_export_sps1_10(self, lang, page_size):
        """Exports the report in PDF format."""
        nb_page = (len(self.branch_report) - 1) // page_size + 1
        data = self._serialize(page_size, nb_page)
        self.pdf_export(
            data,
            f"sps1_10_main_{lang}",
            f"out_sps1_10_{lang}.pdf",
            additional_content=f"_{lang}",
            detail_type=f"sps1_10_detail_{lang}",
            nb_pages=nb_page,
        )

    def pdf_export_sps1_10_th(self):
        """Exports the PDF in Thai."""
        self.ensure_one()
        self.pdf_export_sps1_10(lang="th", page_size=10)

    def pdf_export_sps1_10_en(self):
        """Exports the PDF in English."""
        self.ensure_one()
        self.pdf_export_sps1_10(lang="en", page_size=12)

    def build_file_name(self, file_type, i="") -> str:
        """Build the file name for the report"""
        now = datetime.now()
        unique_no = f"_{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}"
        return f"SPS1-10_{self.year}_{self.company_id.name}{i}{unique_no}.pdf"


class ThailandSPS1_10Line(models.Model):
    _name = "thailand.sps1.10.branch.report"
    _inherit = "thailand.compliance.common.line"
    _description = "SPS1_10 Line"

    sps1_10_id = fields.Many2one("thailand.sps1.10", string="SPS1-10")
    id_nb = fields.Char(
        string="ID Number",
        help="(For foreigners, social security number)",
        compute="_compute_id_nb",
        store=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Employee")
    actual_wages = fields.Monetary(string="Actual Wages")
    contribution = fields.Integer(
        string="Contribution",
        help="{}{}".format(
            "(The fee used in the calculation is not less than ",
            "1, 650 baht and not more than 15, 000 baht)",
        ),
    )

    @api.depends("employee_id")
    def _compute_id_nb(self):
        """The ID number is the identification ID of the employee."""
        for rec in self:
            if rec.employee_id.country_id and rec.employee_id.country_id.code == "TH":
                rec.id_nb = rec.employee_id.format_pid()
            else:
                rec.id_nb = rec.employee_id.format_ss_no()

    def _serialize(self, n, p):
        return {
            f"number_{n}_{p}": str(n),
            f"id_nb_{n}_{p}": self.id_nb,
            f"employee_name_{n}_{p}": self.employee_id.name,
            f"wage_{n}_{p}": self.actual_wages,
            f"baht_contribution_{n}_{p}": self.contribution,
        }
