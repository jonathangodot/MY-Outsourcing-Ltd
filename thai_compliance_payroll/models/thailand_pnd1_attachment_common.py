from odoo import api, fields, models, _
from ..utils.const import PND1_LINES
import logging

_logger = logging.getLogger(__name__)


class ThailandPND1Line(models.AbstractModel):
    _name = "thailand.pnd1.line.common"
    _inherit = "thailand.compliance.common.line"
    _description = "PND1 Line Common"

    income_type = fields.Selection(PND1_LINES, string="Income Type", readonly=True)
    nb_persons = fields.Integer(
        string="Number of Persons", compute="_compute_line", store=True
    )
    income_amount = fields.Monetary(
        string="Income Amount", compute="_compute_line", store=True
    )
    tax_withheld = fields.Monetary(
        string="Tax Withheld", compute="_compute_line", store=True
    )

    def _serialize(self):
        """Serialize the PND1 report to be sent to the API"""
        self.ensure_one()
        serialized = {
            f"no_persons_{self.income_type}": self.nb_persons,
            f"income_amount_{self.income_type}": self.income_amount
            if self.income_amount
            else 0,
            f"tax_amount_{self.income_type}": self.tax_withheld
            if self.tax_withheld
            else 0,
        }
        return serialized

    @api.depends("income_type")
    def _compute_line(self):
        """Compute the line for the PND1 detail report by calling the method according to the income type"""
        for rec in self:
            (
                rec.nb_persons,
                rec.income_amount,
                rec.tax_withheld,
                rec.attachment_line,
            ) = eval(f"rec.compute_line_{rec.income_type}()")

    def compute_line_1(self):
        self.ensure_one()
        return self.compute_from_attachment_line(tax_3_percent=False)

    def compute_line_2(self):
        self.ensure_one()
        return self.compute_from_attachment_line(tax_3_percent=True)

    def compute_line_3(self):
        self.ensure_one()
        return 0, 0, 0, []

    def compute_line_4(self):
        self.ensure_one()
        return 0, 0, 0, []

    def compute_line_5(self):
        self.ensure_one()
        return 0, 0, 0, []

    def compute_line_values(self, attachment_lines):
        income_amount, tax_withheld, rec_attachment_lines = 0, 0, []
        for line in attachment_lines:
            income_amount += line.amount_paid
            tax_withheld += line.tax_withheld
            rec_attachment_lines.append(line.id)
        return income_amount, tax_withheld, rec_attachment_lines


class ThailandPND1AttachmentLineCommon(models.AbstractModel):
    _name = "thailand.pnd1.attachment.line.common"
    _description = "PND1 Attachment Line Common"
    _inherit = "thailand.compliance.common.line"

    conditions = [
        ("1", "Deducted at source"),
        ("2", "Paid tax for recipient every time"),
        ("3", "Paid tax for recipient one time"),
    ]

    employee_id = fields.Many2one("hr.employee", string="Employee")
    condition = fields.Selection(conditions, string="Condition", default="1")
    employee_name = fields.Char(
        string="Employee Name", related="employee_id.given_names"
    )
    employee_surname = fields.Char(
        string="Employee Surname", related="employee_id.family_name"
    )
    employee_position = fields.Char(
        string="Position", related="employee_id.job_id.name"
    )
    amount_paid = fields.Monetary(string="Amount Paid (GROSS)")
    tax_withheld = fields.Monetary(string="Tax Withheld")

    def _serialize(self, n, p):
        """Serialize the PND1 report to be sent to the PDF form"""
        return {
            f"number_{n}_{p}": n,
            f"recipient_name_{n}_{p}": self.employee_name,
            f"recipient_surname_{n}_{p}": self.employee_surname
            if self.employee_surname
            else self.employee_id.name,
            f"recipient_pin_{n}_{p}": self.employee_id.format_pid(),
            f"recipient_tin_{n}_{p}": self.employee_id.tin,
            f"amount_paid_{n}_{p}": self.amount_paid if self.amount_paid else "",
            f"tax_withheld_{n}_{p}": self.tax_withheld if self.tax_withheld else "",
            f"condition_{n}_{p}": self.condition,
        }
