from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.thai_compliance.utils.fill_pdf import fill_pdf
import string

from ..utils.const import WTC_LINES

import os
import logging

_logger = logging.getLogger(__name__)


class ThailandWithholdingTaxCertificate(models.Model):
    _name = "thailand.withholding.tax.certificate"
    _inherit = "thailand.compliance.payroll.common"
    _description = "Withholding Tax Certificate"
    _order = "employee_id desc"

    payers = [
        ("source", "(1) Withhold at source"),
        ("every_time", "(2) Pay every time"),
        ("one_time", "(3) Pay one time"),
        ("other", "(4) Other (Please Secify)"),
    ]

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    line = fields.One2many(
        "thailand.withholding.tax.certificate.line", "wtc_id", string="Line"
    )
    amount_paid_to_fund = fields.Monetary(
        string="Gvt. Pension Fund",
        help="Amount paid to Government Pension Fund / Government Permanent Employee Fund / Private Teachers Aid Fund",
    )
    amount_paid_to_social_security = fields.Monetary(
        string="SS Fund", help="Amount paid to Social Security Fund"
    )
    amount_paid_to_providient_fund = fields.Monetary(
        string="Providient Fund", help="Amount paid to Provident Fund"
    )
    payer = fields.Selection(payers, string="Payer", default="source")
    payer_other = fields.Char(string="Payer Other")
    tot_income = fields.Monetary(
        string="Total Income", compute="_compute_tot_income", store=True
    )
    tot_tax_paid = fields.Monetary(
        string="Total Tax Paid", compute="_compute_tot_tax_paid", store=True
    )
    book_no = fields.Integer(string="Book No.")
    no = fields.Integer(string="No")
    seq_no = fields.Integer(string="Seq. No.")
    pnd1a = fields.Boolean(string="PND1A", default=False)
    pnd1a_ex = fields.Boolean(string="PND1A Ex", default=False)
    pnd2 = fields.Boolean(string="PND2", default=False)
    pnd2a = fields.Boolean(string="PND2A", default=False)
    pnd3 = fields.Boolean(string="PND3", default=False)
    pnd3a = fields.Boolean(string="PND3A", default=False)
    pnd53 = fields.Boolean(string="PND53", default=False)

    def _serialize(self, lang):
        """Serialize data for PDF export"""
        self.ensure_one()
        serialized = self.serialize()
        serialized.update(
            {
                # Header
                "book_no": self.book_no,
                "no": self.no,
                # Employee info
                "employee_name": self.employee_id.name,
                "employee_address": self.employee_id.format_address(),
                "employee_pid": self.employee_id.format_pid(),
                "employee_tin": self.employee_id.format_tin(),
                # WTC info
                "seq_no": self.seq_no,
                "pnd1a": "✓" if self.pnd1a else "",
                "pnd1a_ex": "✓" if self.pnd1a_ex else "",
                "pnd2": "✓" if self.pnd2 else "",
                "pnd2a": "✓" if self.pnd2a else "",
                "pnd3": "✓" if self.pnd3 else "",
                "pnd3a": "✓" if self.pnd3a else "",
                "pnd53": "✓" if self.pnd53 else "",
                # Tax info
                "other_fund": self.amount_paid_to_fund,
                "social_security_fund": self.amount_paid_to_social_security,
                "provident_fund": self.amount_paid_to_providient_fund,
                "payer_1": "✓" if self.payer == "source" else "",
                "payer_2": "✓" if self.payer == "every_time" else "",
                "payer_3": "✓" if self.payer == "one_time" else "",
                "payer_4": "✓" if self.payer == "other" else "",
                "payer_specify": self.payer_other,
                "total_amount": self.tot_income,
                "total_tax_withheld": self.tot_tax_paid,
                "tot_withholding_tax_in_letter": self.amount_in_letter(
                    self.tot_tax_paid, lang
                ),
            }
        )
        for line in self.line:
            serialized.update(line.serialize())
        serialized = self.format_serialized_float(serialized, decompose=True)
        serialized = self.clean_serialized(serialized)
        return serialized

    @api.depends("line")
    def _compute_tot_income(self):
        """Compute total income of the employee for this year"""
        for rec in self:
            rec.tot_income = sum([line.amount_paid for line in rec.line])

    @api.depends("line")
    def _compute_tot_tax_paid(self):
        """Compute total tax paid of the employee for this year"""
        for rec in self:
            rec.tot_tax_paid = sum([line.tax_withheld for line in rec.line])

    def pdf_export_wtc(self, lang):
        """Export WTC to PDF"""
        self.ensure_one()
        data = self._serialize(lang)
        self.pdf_export(
            data,
            f"withholding_tax_certificate_{lang}",
            f"wtc_{lang}.pdf",
            f"_{self.employee_id.name.replace(' ', '_')}_{lang}",
        )

    def pdf_export_wtc_en(self):
        """Export WTC to PDF in English"""
        self.ensure_one()
        self.pdf_export_wtc(lang="en")

    def pdf_export_wtc_th(self):
        """Export WTC to PDF in Thai"""
        self.ensure_one()
        self.pdf_export_wtc(lang="th")

    def fetch_duplicate(self):
        """Fetch duplicate WTC"""
        self.ensure_one()
        return self.search(
            [
                ("company_id", "=", self.company_id.id),
                ("year", "=", self.year),
                ("employee_id", "=", self.employee_id.id),
            ]
        )


class ThailandWTCLine(models.Model):
    _name = "thailand.withholding.tax.certificate.line"
    _inherit = "thailand.compliance.common.line"
    _description = "Withholding Tax Certificate Line"
    _order = "name asc"

    wtc_id = fields.Many2one("thailand.withholding.tax.certificate", string="WTC")
    name = fields.Selection(WTC_LINES, string="Name")
    specify = fields.Char(string="Specify...")
    amount_paid = fields.Monetary(string="Amount Paid")
    tax_withheld = fields.Monetary(string="Tax Withheld")
    date_paid = fields.Date(string="Date Paid")

    def serialize(self):
        """Serialize data for PDF export"""
        self.ensure_one()
        serialized = super().serialize()
        i = str(string.ascii_lowercase.index(self.name) + 1)
        serialized.update(
            {
                "name": self.name,
                f"specify{i}": self.specify,
                f"amount{i}": self.amount_paid,
                f"tax_withheld{i}": self.tax_withheld,
                f"date_paid{i}": self.date_paid if self.date_paid else "",
            }
        )
        return serialized

    @api.constrains("tax_withheld")
    def _tax_smaller_than_amount(self):
        """Makes sure an employee didn't pay more tax than he earned"""
        for rec in self:
            if rec.tax_withheld > rec.amount_paid:
                raise ValidationError(
                    _("Tax Withheld cannot be greater than Amount Paid.")
                )
