from odoo import api, fields, models, _
from ..utils.const import MONTHS
from datetime import date
from odoo.addons.thai_compliance.utils.fill_pdf import fill_pdf

import os
import logging

_logger = logging.getLogger(__name__)


class ThailandPND1Month(models.Model):
    _name = "thailand.pnd1.month"
    _inherit = "thailand.compliance.payroll.common"
    _description = "PND1 Monthly Report"
    _order = "year desc, month asc"

    pnd1_year_company = fields.Many2one(
        "thailand.pnd1.year.company", string="Year PND1"
    )
    detail_lines = fields.One2many(
        "thailand.pnd1.month.line", "pnd1_month_id", string="Detail"
    )
    attachment_line = fields.One2many(
        "thailand.pnd1.attachment.line", "pnd1_month_id", string="Attachment"
    )
    tot_amount_paid = fields.Monetary(
        string="Total Amount Paid", compute="_compute_tot_amount_paid", store=True
    )
    tot_tax_withheld = fields.Monetary(
        string="Total Tax Withheld", compute="_compute_tot_tax_withheld", store=True
    )
    nb_of_employees = fields.Integer(
        string="Number of Employees", compute="_compute_nb_of_employees", store=True
    )
    month = fields.Selection(
        MONTHS, string="Month", default=str(date.today().month), required=True
    )
    filling_type = fields.Selection(
        [("Ord", "Ordinary"), ("Add", "Additional")],
        string="Filling Type",
        default="Ord",
        required=True,
    )
    filling_no_time = fields.Integer(string="Filling No.", default="1")
    receipt_date = fields.Date(string="Receipt Date")
    receipt_no = fields.Char(string="Receipt No.")
    receipt_amount = fields.Monetary(string="Receipt Amount")
    receipt_amount_in_letter = fields.Char(
        string="Receipt Amount in Letter",
        compute="_compute_receipt_amount_in_letter",
        store=True,
    )
    attachment_type = fields.Selection(
        [("Attachment", "Attachment"), ("Diskette", "Diskette")],
        string="Attachment Type",
        default="Attachment",
    )
    nb_pages = fields.Integer(string="Number of Pages", default=1)
    control_no = fields.Char(string="Control No.")

    accordance_help_string = "{}{}".format(
        "For : Income under Section 40 (1): salaries, wages, etc. in the case where ",
        "the Revenue Department has given approval to apply 3% withholding tax",
    )

    accordance_doc_no = fields.Char(
        string="Accordance Doc No.",
        help=accordance_help_string,
    )
    accordance_doc_date = fields.Date(
        string="Accordance Doc Date", help=accordance_help_string
    )
    surcharge = fields.Monetary(string="Surcharge")

    def _serialize(self, max_item, lang):
        """Serialize the PND1 report to be sent to the PDF generator"""
        self.ensure_one()
        serialized = self.serialize()
        serialized.update(
            {
                #
                "filling_type_ordinary": "✓" if self.filling_type == "Ord" else "",
                "filling_type_additional": "✓" if self.filling_type == "Add" else "",
                "filling_no_time": self.filling_no_time
                if self.filling_type == "Add"
                else "",
                #
                "year_of_payment": self.year_be,
                "month_1": "✓" if self.month == "1" else "",
                "month_2": "✓" if self.month == "2" else "",
                "month_3": "✓" if self.month == "3" else "",
                "month_4": "✓" if self.month == "4" else "",
                "month_5": "✓" if self.month == "5" else "",
                "month_6": "✓" if self.month == "6" else "",
                "month_7": "✓" if self.month == "7" else "",
                "month_8": "✓" if self.month == "8" else "",
                "month_9": "✓" if self.month == "9" else "",
                "month_10": "✓" if self.month == "10" else "",
                "month_11": "✓" if self.month == "11" else "",
                "month_12": "✓" if self.month == "12" else "",
                #
                "receipt_date": self.receipt_date,
                "receipt_no": self.receipt_no,
                "receipt_amount": self.receipt_amount if self.receipt_amount else "",
                "receipt_amount_in_letter": self.receipt_amount_in_letter
                if self.receipt_amount > 0
                else "",
                #
                "attachment_selection_attachment": "✓"
                if self.attachment_type == "Attachment"
                else "",
                "attachment_selection_diskette": "✓"
                if self.attachment_type == "Diskette"
                else "",
                "attachment_nb_pages": str(self.nb_pages)
                if self.attachment_type == "Attachment"
                else "",
                "diskette_nb_pages": str(self.nb_pages)
                if self.attachment_type == "Diskette"
                else "",
                "control_no": self.control_no,
                #
                "accordance_doc_no": self.accordance_doc_no,
                "accordance_doc_date": self.accordance_doc_date,
                "income_amount_6": self.tot_amount_paid,
                "tax_amount_6": self.tot_tax_withheld,
                "no_persons_6": self.nb_of_employees,
                "tax_amount_7": self.surcharge,
                "tax_amount_total": self.tot_tax_withheld + self.surcharge,
                "withholding_tax_in_letter": self.amount_in_letter(
                    self.tot_tax_withheld, "en"
                ),
                # For attachment
                "amount_paid_tot": self.tot_amount_paid,
                "tax_withheld_tot": self.tot_tax_withheld + self.surcharge,
                # For PND1, building and village are on the same field
                "address_building": "{} {} {}".format(
                    self.company_id.building if self.company_id.building else "",
                    "/"
                    if self.company_id.building
                    and self.company_id.village
                    and lang == "en"
                    else "",
                    self.company_id.village
                    if self.company_id.village and lang == "en"
                    else "",
                ),
            }
        )

        serialized.update(
            self.serialize_pnd1_pages(max_item, self.detail_lines, serialized)
        )
        serialized.update(
            self.serialize_income_type_lines(self.detail_lines, serialized)
        )

        serialized = self.format_serialized_float(
            serialized, decompose=True if lang == "th" else False
        )
        serialized = self.clean_serialized(serialized)
        return serialized

    @api.depends("receipt_amount")
    def _compute_receipt_amount_in_letter(self):
        """Convert the receipt amount to Thai Baht in letter"""
        for rec in self:
            lang = self.env.context["lang"] if "lang" in self.env.context else "en_US"
            rec.receipt_amount_in_letter = rec.amount_in_letter(
                rec.receipt_amount, "th" if lang == "th_TH" else "en"
            )

    @api.depends("attachment_line.amount_paid")
    def _compute_tot_amount_paid(self) -> None:
        """Compute the total amount paid from attachment lines"""
        for rec in self:
            rec.tot_amount_paid = sum(
                [employee.amount_paid for employee in rec.attachment_line]
            )

    @api.depends("attachment_line.tax_withheld")
    def _compute_tot_tax_withheld(self) -> None:
        """Compute the total tax withheld from attachment lines"""
        for rec in self:
            rec.tot_tax_withheld: float = sum(
                [employee.tax_withheld for employee in rec.attachment_line]
            )

    @api.depends("attachment_line")
    def _compute_nb_of_employees(self):
        """Compute the number of employees from attachment lines"""
        for rec in self:
            rec.nb_of_employees = len(rec.attachment_line)

    def fetch_duplicate(self) -> None:
        """Fetch duplicates of the PND1 report"""
        self.ensure_one()
        return self.search(
            [
                ("company_id", "=", self.company_id.id),
                ("month", "=", self.month),
                ("year", "=", self.year),
            ]
        )

    def new_attachment_line(self, payslip):
        """Create a new attachment line from a payslip and attach it to the PND1"""
        new_line = self.env["thailand.pnd1.attachment.line"].create(
            {
                "employee_id": payslip.employee_id.id,
                "payslip_ids": [(4, payslip.id)],
                "payment_date": payslip.date_to,
                "amount_paid": payslip.line_ids.filtered(
                    lambda l: l.code == self.code_settings()["code_gross"]
                ).total,
                "tax_withheld": -payslip.line_ids.filtered(
                    lambda l: l.code == self.code_settings()["code_tax"]
                ).total,
                "pnd1_month_id": self.id,
                "year": self.year,
            }
        )
        self.get_custom_fields(payslip, new_line)

    def add_to_attachment_line(self, payslip, attachment_line):
        """Add the payslip to an existing attachment line"""
        attachment_line.payslip_ids = [(4, payslip.id)]
        attachment_line.amount_paid += payslip.line_ids.filtered(
            lambda l: l.code == self.code_settings()["code_gross"]
        ).total
        attachment_line.tax_withheld += -payslip.line_ids.filtered(
            lambda l: l.code == self.code_settings()["code_tax"]
        ).total
        self.get_custom_fields(payslip, attachment_line)

    def get_custom_fields(self, payslip, new_line):
        """Compute the custom fields and attach them to the attachment line"""
        for field in self.env["hr.payroll.report.income.type"].search([]):
            for rule in field.salary_rule:
                new_line.write(
                    {
                        field.model_field_name: payslip.line_ids.filtered(
                            lambda l: l.code == rule.code
                        ).total
                    }
                )

    def new_detail_line(self, i):
        """Create a new detail line attach it to the PND1"""
        self.detail_lines += self.env["thailand.pnd1.month.line"].create(
            {"income_type": str(i)}
        )

    def create_record(self) -> None:
        """Creates the record for the PND1 report, line by line, then compute the total."""
        self.ensure_one()
        for payslip in self.associated_payslips(
            start_month=int(self.month), end_month=int(self.month)
        ):
            attachment_line = self.env["thailand.pnd1.attachment.line"].search(
                [
                    ("employee_id", "=", payslip.employee_id.id),
                    ("pnd1_month_id", "=", self.id),
                ]
            )
            if len(attachment_line) == 0:
                self.new_attachment_line(payslip)
            else:
                self.add_to_attachment_line(payslip, attachment_line)

        for i in range(1, 6):
            self.new_detail_line(i)

    def generate_report(self) -> None:
        """Reset the report and generate it again"""
        for rec in self:
            rec.tot_amount_paid, rec.tot_tax_withheld, rec.nb_of_employees = 0, 0, 0
            rec.attachment_line.unlink()
            rec.detail_lines.unlink()
            rec.create_record()

    def pdf_export_pnd1_month_en(self):
        """Export the PND1 report in English"""
        self.ensure_one()
        self.pdf_export_pnd1_month(lang="en", max_item=7)

    def pdf_export_pnd1_month_th(self):
        """Export the PND1 report in Thai"""
        self.ensure_one()
        self.pdf_export_pnd1_month(lang="th", max_item=8)

    def pdf_export_pnd1_month(self, lang, max_item) -> None:
        """Generate the PDF for the PND1 report for company"""
        data = self._serialize(max_item, lang)
        self.pdf_export(
            data,
            f"pnd1_{lang}",
            f"out_pnd1_file_{lang}.pdf",
            detail_type=f"pnd1_attachment_{lang}",
            nb_pages=int(data["page_tot"]),
        )


class ThailandPND1Line(models.Model):
    _name = "thailand.pnd1.month.line"
    _inherit = "thailand.pnd1.line.common"
    _description = "PND1 Monthly Report Line"

    pnd1_month_id = fields.Many2one("thailand.pnd1.month", string="PND1 Month")
    attachment_line = fields.One2many(
        "thailand.pnd1.attachment.line", "pnd1_line_id", string="Attachment Line"
    )

    def compute_from_attachment_line(self, tax_3_percent=False):
        """Compute the line from the attachment line"""
        self.ensure_one()
        attachment_lines = self.env["thailand.pnd1.attachment.line"].search(
            [
                ("pnd1_month_id", "=", self.pnd1_month_id.id),
                ("payslip_ids.struct_id.type_id.tax_3_percent", "=", tax_3_percent),
            ]
        )
        income_amount, tax_withheld, rec_attachment_lines = self.compute_line_values(
            attachment_lines
        )
        return len(attachment_lines), income_amount, tax_withheld, rec_attachment_lines


class ThailandPND1AttachmentLine(models.Model):
    _name = "thailand.pnd1.attachment.line"
    _inherit = "thailand.pnd1.attachment.line.common"
    _description = "PND1 Monthly Report Employee Detail"

    payslip_ids = fields.One2many("hr.payslip", "pnd1_month", string="Payslip")

    payment_date = fields.Date(string="Payment Date")
    pnd1_month_id = fields.Many2one(
        "thailand.pnd1.month", string="PND1 Month Employees"
    )
    pnd1_line_id = fields.Many2one("thailand.pnd1.month.line", string="PND1 Line")

    def _serialize(self, n, p):
        """Serialize the PND1 attachment lines to a dict where the keys are the fields of the PDF"""
        self.ensure_one()
        serialized = super()._serialize(n, p)
        serialized.update({f"payment_date_{n}_{p}": self.payment_date})
        return serialized
