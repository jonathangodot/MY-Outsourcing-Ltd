from odoo.tests import tagged
from .common import TestThaiCompliancePayrollCommon
from ..utils.const import *
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_payroll_pnd1_year", "newlogic", "thai_compliance")
class TestThailandPND1Year(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestThailandPND1Year, self).setUpClass()
        self.pnd1_july.generate_report()
        self.pnd1_august.generate_report()
        self.pnd1_2021 = self.pnd1_year_obj.create(
            {
                "company_id": self.company_kaamelott.id,
                "year": 2021,
            }
        )

    def test_generate_report(self):
        self.pnd1_2021.generate_report()
        self.assertEqual(self.pnd1_2021.number_of_employees, 8)
        self.assertEqual(self.pnd1_2021.tot_employee_income, 76000)
        self.assertEqual(self.pnd1_2021.tot_tax_withheld, 0)
        self.assertEqual(len(self.pnd1_2021.pnd1_month), 2)
        self.assertEqual(len(self.pnd1_2021.line), 5)
        self.assertEqual(len(self.pnd1_2021.attachment_line), 8)
        # F*** Odoo of Schrödinger
        # _logger.info(
        #     f"Year : {self.pnd1_2021.id}, company : {self.pnd1_2021.company_id.id}"
        # )
        line1 = self.env["thailand.pnd1.year.line"].search(
            [("pnd1_year", "=", self.pnd1_2021.id), ("income_type", "=", "1")]
        )
        self.assertEqual(line1.nb_persons, 6)
        self.assertEqual(line1.income_amount, 42000)
        self.assertEqual(line1.tax_withheld, 0)
        line2 = self.env["thailand.pnd1.year.line"].search(
            [("pnd1_year", "=", self.pnd1_2021.id), ("income_type", "=", "2")]
        )
        self.assertEqual(line2.nb_persons, 2)
        self.assertEqual(line2.income_amount, 34000)
        self.assertEqual(line2.tax_withheld, 0)

        arthur_line = self.env["thailand.pnd1.year.attachment.line"].search(
            [
                ("pnd1_year", "=", self.pnd1_2021.id),
                ("employee_id", "=", self.arthur.id),
            ]
        )
        self.assertEqual(arthur_line.amount_paid, 2000)
        self.assertEqual(arthur_line.tax_withheld, 0)
        lancelot_line = self.env["thailand.pnd1.year.attachment.line"].search(
            [
                ("pnd1_year", "=", self.pnd1_2021.id),
                ("employee_id", "=", self.lancelot.id),
            ]
        )
        self.assertEqual(lancelot_line.amount_paid, 6000)
        self.assertEqual(lancelot_line.tax_withheld, 0)

    def test_generate_withholding_tax(self):
        self.pnd1_july.generate_report()
        self.pnd1_august.generate_report()
        self.pnd1_2021.generate_report()
        self.pnd1_2021.generate_withholding_tax_certificates()

        wtcs = self.env["thailand.withholding.tax.certificate"].search(
            [("employee_id", "in", [employee.id for employee in self.test_employees])]
        )
        wtc_lancelot = self.env["thailand.withholding.tax.certificate"].search(
            [("employee_id", "=", self.lancelot.id)]
        )

        self.assertEqual(len(wtcs), 8)
        self.assertEqual(wtc_lancelot.tot_income, 6000)
        self.assertEqual(wtc_lancelot.tot_tax_paid, 0)
        self.assertEqual(len(wtc_lancelot.line), 15)
        self.assertEqual(wtc_lancelot.line[0].amount_paid, 6000)
