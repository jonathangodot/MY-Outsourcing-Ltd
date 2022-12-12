from odoo import fields, models, _, api
from odoo.exceptions import UserError
from ..utils.const import PND1_LINES
import string

import logging

_logger = logging.getLogger(__name__)


class ThailandPND1YearCompany(models.Model):
    _name = "thailand.pnd1.year.company"
    _inherit = "thailand.compliance.payroll.common"
    _description = "PND1 Year Company"
    _order = "year desc"

    number_of_employees = fields.Integer(
        string="Number of Employees", compute="_compute_number_of_employees", store=True
    )
    tot_employee_income = fields.Monetary(
        string="Total Employee Income",
        compute="_compute_tot_employee_income",
        store=True,
        readonly=True,
    )
    tot_tax_withheld = fields.Monetary(
        string="Total Tax Withheld",
        compute="_compute_tot_tax_withheld",
        store=True,
        readonly=True,
    )
    pnd1_month = fields.One2many(
        "thailand.pnd1.month", "pnd1_year_company", string="Detail"
    )
    line = fields.One2many("thailand.pnd1.year.line", "pnd1_year", string="Line")
    attachment_line = fields.One2many(
        "thailand.pnd1.year.attachment.line",
        "pnd1_year",
        string="Attachment Line",
    )
    tax_item = fields.Char(string="Tax Item")
    accordance_doc_no = fields.Char(string="Accordance Doc No", help="For line 2.")
    accordance_doc_date = fields.Date(string="Accordance Doc Date", help="For line 2.")
    filling_type = fields.Selection(
        [("ORDINARY", "Ordinary"), ("ADDITIONAL", "Additional")],
        string="Filling Type",
        default="ORDINARY",
    )
    no_additional_time = fields.Integer(string="No. of Additional Time", default=0)

    @api.depends("attachment_line")
    def _compute_number_of_employees(self):
        """Compute the number of employees"""
        for rec in self:
            rec.number_of_employees = len(rec.attachment_line)

    @api.depends("attachment_line")
    def _compute_tot_employee_income(self):
        """Compute the total employee income"""
        for rec in self:
            rec.tot_employee_income = sum(rec.attachment_line.mapped("amount_paid"))

    @api.depends("attachment_line")
    def _compute_tot_tax_withheld(self):
        """Compute the total tax withheld"""
        for rec in self:
            rec.tot_tax_withheld = sum(rec.attachment_line.mapped("tax_withheld"))

    def _serialize(self):
        """Serialize the data to be used in the report"""

        def serialize_income_type(income_type: int, page: int) -> dict:
            """Serialize the income type to fit the PDF form"""
            income_types = {}
            for i in range(1, 6):
                income_types[f"income_type_{i}_{page}"] = (
                    "✓" if income_type == str(i) else ""
                )

            return income_types

        self.ensure_one()
        serialized = self.serialize()
        serialized.update(
            {
                "tax_item": self.tax_item,
                "accordance_doc_no": self.accordance_doc_no,
                "accordance_doc_date": self.accordance_doc_date,
                "no_persons_6": self.number_of_employees,
                "income_amount_6": self.tot_employee_income,
                "tax_amount_6": self.tot_tax_withheld,
                "filling_type_ordinary": "✓" if self.filling_type == "ORDINARY" else "",
                "filling_type_additional": "✓"
                if self.filling_type == "ADDITIONAL"
                else "",
                "no_additionnal_time": self.no_additional_time,
                "attachment_selection_attachment": "✓",
                "attachment_selection_diskette": "",
            }
        )

        serialized.update(self.serialize_pnd1_pages(7, self.line, serialized))
        serialized.update(self.serialize_income_type_lines(self.line, serialized))

        serialized = self.format_serialized_float(serialized, decompose=True)
        serialized = self.clean_serialized(serialized)
        return serialized

    def generate_report(self) -> None:
        """Gets all the informations needed to generate the report and build the Odoo model out of it"""
        for rec in self:
            rec.line.unlink()
            rec.attachment_line.unlink()
            rec.create_record()

    def create_record(self):
        self.ensure_one()
        self.pnd1_month = self.env["thailand.pnd1.month"].search(
            [("year", "=", self.year), ("company_id", "=", self.company_id.id)]
        )

        PND1_month = self.env["thailand.pnd1.month"].search(
            [
                ("year", "=", self.year),
                ("company_id", "=", self.company_id.id),
            ]
        )

        employee_set = set()
        for montly_report in PND1_month:
            employee_set.update(
                set(
                    [employee.employee_id for employee in montly_report.attachment_line]
                )
            )

        self.attachment(employee_set)
        self.detail()

    def attachment(self, employees):
        self.ensure_one()
        for monthly_pnd1 in self.pnd1_month:
            for detail_line in monthly_pnd1.detail_lines:
                for employee_line in detail_line.attachment_line:
                    if (
                        detail_line.income_type
                        == employee_line.pnd1_line_id.income_type
                    ):
                        if employee_line.amount_paid > 0:
                            employee_year_line = self.env[
                                "thailand.pnd1.year.attachment.line"
                            ].search(
                                [
                                    ("employee_id", "=", employee_line.employee_id.id),
                                    ("pnd1_year", "=", self.id),
                                ]
                            )
                            if len(employee_year_line) > 1:
                                raise UserError(
                                    _(
                                        "Something went wrong, please contact your administrator."
                                    )
                                )
                            elif len(employee_year_line) == 0:
                                self.env["thailand.pnd1.year.attachment.line"].create(
                                    {
                                        "pnd1_year": self.id,
                                        "income_type": detail_line.income_type,
                                        "employee_id": employee_line.employee_id.id,
                                        "amount_paid": employee_line.amount_paid,
                                        "tax_withheld": employee_line.tax_withheld,
                                    }
                                )
                            else:
                                employee_year_line.amount_paid += (
                                    employee_line.amount_paid
                                )
                                employee_year_line.tax_withheld += (
                                    employee_line.tax_withheld
                                )

    def detail(self):
        self.ensure_one()
        for income_type in PND1_LINES:
            self.env["thailand.pnd1.year.line"].create(
                {
                    "pnd1_year": self.id,
                    "income_type": income_type[0],
                }
            )

    def generate_withholding_tax_certificates(self):
        """Generate the withholding tax certificates for the year, for all the employees of the company"""

        def create_line(i):
            """Create a line for the withholding tax certificate"""
            (tot_income, tot_tax_paid) = (
                compute_income_and_tax(employee, rec) if i == 0 else (0, 0)
            )
            return self.env["thailand.withholding.tax.certificate.line"].create(
                {
                    "name": string.ascii_lowercase[i],
                    "amount_paid": tot_income,
                    "tax_withheld": tot_tax_paid,
                }
            )

        def compute_income_and_tax(employee, rec):
            """Compute the total amount paid and the total tax withheld"""
            PND1_employee = rec.env["thailand.pnd1.attachment.line"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("year", "=", rec.year),
                ]
            )
            return (
                sum([month.amount_paid for month in PND1_employee]),
                sum([month.tax_withheld for month in PND1_employee]),
            )

        for rec in self:
            employees = self.env["hr.employee"].search(
                [
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            for employee in employees:
                contract = self.fetch_contracts(employee, rec)
                if len(contract) > 0:
                    self.clear_records(
                        employee, rec, "thailand.withholding.tax.certificate"
                    )

                    self.env["thailand.withholding.tax.certificate"].create(
                        {
                            "employee_id": employee.id,
                            "year": rec.year,
                            "amount_paid_to_social_security": rec.count_payslip_line(
                                employee,
                                "code_secu",
                                True,
                                "previous_social_security",
                            ),
                            "amount_paid_to_providient_fund": employee.provident_fund,
                            "payer": "source",
                            "line": [create_line(i).id for i in range(0, 15)],
                        }
                    )

    def pdf_export_pnd1_year(self):
        """Export the report to a PDF file"""
        self.ensure_one()
        data = self._serialize()
        self.pdf_export(
            data,
            "pnd1_kor_th",
            "out_pnd1_year_file.pdf",
            additional_content=f"_{self.company_id.name}",
            detail_type="pnd1_kor_attachment_th",
            nb_pages=int(data["page_tot"]),
        )


class ThailandPND1YearLine(models.Model):
    _name = "thailand.pnd1.year.line"
    _inherit = "thailand.pnd1.line.common"
    _description = "PND1 Year Line"

    pnd1_year = fields.Many2one("thailand.pnd1.year.company", string="PND1 Year")
    attachment_line = fields.One2many(
        "thailand.pnd1.year.attachment.line",
        "pnd1_year_line",
        string="Attachment Line",
    )

    def compute_from_attachment_line(self, tax_3_percent=False):
        """Compute the income type total from attachment lines of monthly PND1s"""
        self.ensure_one()
        attachment_lines = self.env["thailand.pnd1.year.attachment.line"].search(
            [
                ("pnd1_year", "=", self.pnd1_year.id),
                ("company_id", "=", self.pnd1_year.company_id.id),
                ("income_type", "=", self.income_type),
            ]
        )
        income_amount, tax_withheld, rec_attachment_lines = self.compute_line_values(
            attachment_lines
        )
        return len(attachment_lines), income_amount, tax_withheld, rec_attachment_lines


class ThailandPND1YearAttachmentLine(models.Model):
    _name = "thailand.pnd1.year.attachment.line"
    _inherit = "thailand.pnd1.attachment.line.common"
    _description = "PND1 Year Attachment Line"

    pnd1_year = fields.Many2one("thailand.pnd1.year.company", string="PND1 Year")
    pnd1_year_line = fields.Many2one("thailand.pnd1.year.line", string="PND1 Year Line")
    pnd1_month_attachment_line = fields.Many2one(
        "thailand.pnd1.attachment.line.common",
        string="PND1 Month",
    )
    employee_address = fields.Char(
        string="Employee Address",
        related="employee_id.address_home_id.street",
    )
    income_type = fields.Selection(PND1_LINES, string="Income Type", readonly=True)

    def _serialize(self, n, p):
        """Serialize the PND1 kor attachment lines to a dict where the keys are the fields of the PDF"""
        self.ensure_one()
        serialized = super()._serialize(n, p)
        serialized.update({f"employee_address_{n}_{p}": self.employee_address})
        serialized.update({f"recipient_address_{n}_{p}": f"Employee address {n} {p}"})
        return serialized
