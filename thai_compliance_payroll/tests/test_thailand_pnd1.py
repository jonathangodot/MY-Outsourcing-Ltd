from odoo.tests import tagged
from odoo.exceptions import ValidationError
from .common import TestThaiCompliancePayrollCommon
from ..utils.const import *
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_payroll_pnd1", "newlogic", "thai_compliance")
class TestThailandPND1(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestThailandPND1, self).setUpClass()

    def test_compute_methodes(self):
        self.pnd1_july.generate_report()
        self.assertEqual(
            self.pnd1_july.year_be,
            "2564",
            "Year BE should be computed correctly",
        )
        self.assertEqual(
            self.pnd1_july.receipt_amount_in_letter,
            "Zero Baht",
            "Receipt amount in letter should be computed correctly",
        )
        self.assertEqual(
            self.pnd1_july.tot_amount_paid,
            38000,
            "Total amount paid should be computed correctly",
        )
        self.assertEqual(
            self.pnd1_july.tot_tax_withheld,
            0,
            "Total tax withheld should be computed correctly",
        )
        self.assertEqual(
            self.pnd1_july.nb_of_employees,
            8,
            "Number of employees should be computed correctly",
        )
        with self.assertRaises(ValidationError):
            self.pnd1_month_obj.create(
                {
                    "year": "2021",
                    "month": "7",
                    "company_id": self.company_kaamelott.id,
                }
            )

    def test_generate_report(self):
        self.pnd1_july.generate_report()
        self.assertEqual(len(self.pnd1_july.detail_lines), 5)
        self.assertEqual(len(self.pnd1_july.attachment_line), 8)
        for slip in self.payslip_obj.search([("employee_id", "=", self.yvain.id)]):
            slip.state = "cancel"
        self.pnd1_july.generate_report()
        self.assertEqual(len(self.pnd1_july.detail_lines), 5)
        self.assertEqual(len(self.pnd1_july.attachment_line), 7)

    def test_compute_line(self):
        self.pnd1_july.generate_report()
        for line in self.pnd1_july.detail_lines:
            if line.income_type == "1":
                self.assertEqual(line.income_amount, 21000)
            elif line.income_type == "2":
                self.assertEqual(line.income_amount, 17000)
            else:
                self.assertEqual(line.income_amount, 0)
