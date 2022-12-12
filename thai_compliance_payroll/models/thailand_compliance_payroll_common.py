from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ThaiCompliancePayrollCommon(models.AbstractModel):
    _name = "thailand.compliance.payroll.common"
    _inherit = "thailand.compliance.common"
    _description = "Common fields for the Thai compliance payroll documents"

    def count_payslip_line(
        self,
        employee,
        code,
        report_is_for_employee=True,
        previous_company_amount_attribute=None,
    ) -> float:
        """Adds the total of specific lines in an employee payslip for the year related
        to this record."""
        self.ensure_one()
        amount: float = 0
        if (
            employee.first_year
            and report_is_for_employee
            and previous_company_amount_attribute
        ):
            amount += getattr(employee, previous_company_amount_attribute)

        try:
            datestart = date(int(self.year), int(self.month), 1)
            datestop = (
                date(int(self.year), int(self.month), 1)
                + relativedelta(months=1)
                + timedelta(days=-1)
            )
        except AttributeError:
            datestart = date(int(self.year), 1, 1)
            datestop = date(int(self.year), 12, 31)
        payslips = self.env["hr.payslip"].search(
            [
                ("employee_id", "=", employee.id),
                ("date_from", ">=", datestart),
                ("date_to", "<=", datestop),
            ]
        )
        for payslip in payslips:
            amount += payslip.line_ids.filtered(
                lambda l: l.code == self.code_settings()[code]
            ).total
        return amount

    def code_settings(self):
        """Fetches the code settings"""
        return {
            "code_gross": self.env["ir.config_parameter"].get_param(
                "thai_compliance_payroll.code_gross"
            ),
            "code_tax": self.env["ir.config_parameter"].get_param(
                "thai_compliance_payroll.code_tax"
            ),
            "code_secu": self.env["ir.config_parameter"].get_param(
                "thai_compliance_payroll.code_secu"
            ),
        }

    def serialize_pnd1_pages(self, max_item, income_type_lines, serialized):
        """Serialize the lines of the PND1 attachment pages report"""

        def serialize_income_type(income_type: int, page: int) -> dict:
            """Serialize the income type to fit the PDF form"""
            income_types = {}
            for i in range(1, 6):
                income_types[f"income_type_{i}_{page}"] = (
                    "✓" if income_type == str(i) else ""
                )
            return income_types

        def incr_page(page_no):
            return 0, page_no + 1

        def get_page_tot(max_item, income_type_lines):
            page_tot = 0
            for income_type in income_type_lines:
                if len(income_type.attachment_line) > 0:
                    page_tot += (len(income_type.attachment_line) // (max_item + 1)) + 1
            return page_tot

        n_in_page, page_no = 0, 1
        for income_type in income_type_lines:
            if len(income_type.attachment_line) > 0:
                for line in income_type.attachment_line:
                    n_in_page += 1
                    serialized.update(line._serialize(n_in_page, page_no))
                    serialized.update({f"page_no_{page_no}": page_no})
                    serialized.update(
                        serialize_income_type(income_type.income_type, page_no)
                    )
                    if n_in_page == max_item:
                        n_in_page, page_no = incr_page(page_no)
                n_in_page, page_no = incr_page(page_no)

        page_tot = get_page_tot(max_item, income_type_lines)
        serialized.update({"page_tot": page_tot})
        return serialized

    def serialize_income_type_lines(self, income_type_lines, serialized):
        """Serialize the lines of the PND1 main page report"""
        for line in income_type_lines:
            serialized.update(line._serialize())
        return serialized
