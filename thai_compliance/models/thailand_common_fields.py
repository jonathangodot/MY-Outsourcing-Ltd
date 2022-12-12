from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import base64
import os
from ..utils.fill_png import fill_pdf

import logging

_logger = logging.getLogger(__name__)


class ThaiComplianceCommon(models.AbstractModel):
    _name = "thailand.compliance.common"
    _inherit = ["mail.thread"]
    _description = "Common fields for the Thai compliance documents"

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
    )
    year = fields.Char(string="Year", default=str(date.today().year), required=True)
    year_be = fields.Char(string="Year BE", compute="_compute_year_be", store=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
    )
    company_address = fields.Char(
        string="Company Address", compute="_compute_address", store=True
    )
    personal_id = fields.Char(string="Company Tax ID", related="company_id.pid")
    taxpayer_id = fields.Char(string="Taxpayer ID Number", related="company_id.tin")
    branch_nb = fields.Integer(
        string="Branch No.",
        related="company_id.branch_nb",
        store=True,
        readonly=True,
    )
    position = fields.Many2one(
        "hr.job",
        compute="_compute_employee_contract",
        store=True,
        readonly=False,
        string="Position of Signer",
    )

    @api.constrains("year", "year_be")
    def _check_year(self):
        """Check that the year is valid"""
        for record in self:
            try:
                int(record.year)
            except ValueError:
                raise ValidationError(_("The year must be a number"))

    @api.depends("year")
    def _compute_year_be(self):
        """Convert the year in Buddhist Era"""
        for rec in self:
            rec.year_be = str(int(rec.year) + 543)

    def format_pid(self, pid) -> str:
        """Format the PID to fit the form"""
        return f"{pid[0]} {pid[1:5]} {pid[5:10]} {pid[10:12]} {pid[12]}" if pid else ""

    def format_tin(self, tin) -> str:
        """Format the TIN to fit the form"""
        return f"{tin[0]} {tin[1:5]} {tin[5:9]} {tin[9]}" if tin else ""

    @api.depends("company_id")
    def _compute_address(self):
        """Compute the address of the company"""
        for rec in self:
            rec.company_address = rec.format_address()

    def format_address(self):
        """Format the address to fit the form"""
        self.ensure_one()
        comp = self.company_id
        return (
            "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, Rm. : {}".format(
                comp.building,
                comp.village,
                comp.address_no,
                comp.address_moo,
                comp.street,
                comp.street2,
                comp.city,
                comp.district,
                comp.province,
                comp.zip,
                comp.room_no,
            )
            .replace("False, ", "")
            .replace(", Rm. : False", "")
        )

    def serialize(self):
        """Serialize the record to a dict where the keys are the field names"""
        self.ensure_one()
        return {
            "year": self.year,
            "company_name": self.company_id.name,
            "company_address": self.format_address(),
            "address_building": self.company_id.building,
            "address_village": self.company_id.village,
            "address_room_no": self.company_id.room_no,
            "address_floor_no": self.company_id.floor,
            "address_no": self.company_id.address_no,
            "address_moo": self.company_id.address_moo,
            "address_street": self.company_id.street,
            "address_road": self.company_id.street2,
            "address_sub_district": self.company_id.city,
            "address_district": self.company_id.district,
            "address_province": self.company_id.province,
            "address_post_code": self.company_id.zip,
            "company_pid": self.format_pid(self.personal_id),
            "company_tin": self.format_tin(self.taxpayer_id),
            "branch_no": self.branch_nb,
            "phone_no": self.company_id.phone,
            "filled_day": date.today().day,
            "filled_month": date.today().month,
            "filled_year": date.today().year + 543,
            "position": self.position.name,
        }

    def clean_serialized(self, serialized):
        """Remove the keys with empty values"""
        return {k: str(v) for k, v in serialized.items() if v and v != 0}

    def format_serialized_float(self, serialized, decompose=False):
        """Format the float fields to fit the form"""
        field_to_decompose = ["amount_paid", "tax_withheld", "contribution", "wage_"]
        serialized_out = serialized.copy()
        for key, value in serialized.items():
            if isinstance(value, float):
                serialized_out[key] = "{:,.2f}".format(value)
                if (
                    decompose
                    and [f in key for f in field_to_decompose]
                    and "fund" not in key
                    and key != "contribution_rate"
                ):
                    decomposed_amount = serialized_out[key].split(".")
                    serialized_out[f"baht_{key}"] = decomposed_amount[0]
                    serialized_out[f"satang_{key}"] = decomposed_amount[1]
                    del serialized_out[key]
            elif isinstance(value, int) and "baht_contribution" in key:
                serialized_out[key] = "{:,}".format(value)
        return serialized_out

    def associated_payslips(self, start_month=1, end_month=12, report="pnd1"):
        """Fetches the payslips associated with the report"""
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date_from", ">=", date(int(self.year), start_month, 1)),
            (
                "date_to",
                "<=",
                date(int(self.year), end_month, 1)
                + relativedelta(months=1)
                + timedelta(days=-1),
            ),
            ("state", "in", ["done", "paid"]),
        ]
        if report == "pnd1":
            domain.append(("struct_id.type_id.count_in_pnd1", "=", True))
        return self.env["hr.payslip"].search(domain)

    @api.constrains("year", "company_id")
    def _check_no_duplicate(self):
        """Check that the month and year are unique"""
        for rec in self:
            if len(rec.fetch_duplicate()) > 1:
                raise ValidationError(_("There is already a record for this document."))

    def fetch_duplicate(self):
        """Fetches duplicates to be overriden for monthly reports"""
        self.ensure_one()
        return self.search(
            [
                ("company_id", "=", self.company_id.id),
                ("year", "=", self.year),
            ]
        )

    def fetch_contracts(self, employee, rec, report="sps1_10") -> None:
        """Fetches the contracts for the employee.
        Contracts considered must be actif"""
        self.ensure_one()
        domain = [
            ("employee_id", "=", employee.id),
            ("state", "not in", ["cancel", "draft"]),
            "|",
            ("date_end", "=", False),
            "|",
            ("date_end", ">=", date(int(rec.year) - 1, 12, 31)),
            ("state", "=", "open"),
        ]
        if report == "sps1_10":
            domain.append(("structure_type_id.count_in_sps1_10", "=", True))
        return self.env["hr.contract"].search(domain)

    def clear_records(self, employee, rec, model) -> None:
        """Clear the model records for the employee and the year"""
        self.env[model].search(
            [
                ("employee_id", "=", employee.id),
                ("year", "=", rec.year),
            ]
        ).unlink()

    def write_pdf(self, file_path, file_name) -> None:
        """Write the pdf to the file system"""
        with open(file_path, "rb") as f:
            file_content = f.read()
            self.env["ir.attachment"].create(
                {
                    "name": file_name,
                    "type": "binary",
                    "datas": base64.b64encode(file_content),
                    "res_model": self._name,
                    "res_id": self.id,
                    "mimetype": "application/pdf",
                    "public": True,
                }
            )

    def pdf_export(
        self,
        data,
        file_type,
        file_path,
        additional_content="",
        detail_type=None,
        nb_pages=0,
    ):
        """Fill the PDF with the serialized values stored in data"""
        self.ensure_one()
        pdf_path = fill_pdf(
            data=data,
            file_type=file_type,
            out_file_name=file_path,
            detail_type=detail_type,
            nb_pages=nb_pages,
        )
        self.write_pdf(
            pdf_path,
            self.build_file_name(file_type, additional_content),
        )
        os.remove(pdf_path)

    def amount_in_letter(self, amount, lang):
        """Converts the amount to a string in the given language"""
        self.ensure_one()
        cur = self.currency_id
        if lang == "th":
            return cur.with_context({"lang": "th_TH"}).amount_to_text(amount)
        else:
            return cur.with_context({"lang": "en_EN"}).amount_to_text(amount)

    def build_file_name(self, file_type, i="") -> str:
        """Build the file name for the report"""
        now = datetime.now()
        unique_no = f"_{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}"
        return f"{file_type}_{self.year}{f'_{self.month}' if hasattr(self, 'month') else ''}{i}{unique_no}.pdf"


class ThaiComplianceCommonLine(models.AbstractModel):
    _name = "thailand.compliance.common.line"
    _inherit = "thailand.compliance.common"
    _description = "Common fields for the Thai compliance documents lines"

    @api.constrains("year", "company_id")
    def _check_no_duplicate(self):
        """No need to check for duplicates on lines"""
        pass


class ThaiComplianceCommonObj(models.Model):
    _inherit = "thailand.compliance.common"
    _name = "thailand.compliance.common.test"
    _description = "Reserved for tests"
