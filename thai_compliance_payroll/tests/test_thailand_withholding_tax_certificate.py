from odoo.tests import tagged
from .common import TestThaiCompliancePayrollCommon
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_payroll_wtc", "newlogic", "thai_compliance")
class TestThailandWTC(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestThailandWTC, self).setUpClass()
        self.wtc_obj = self.env["thailand.withholding.tax.certificate"]
        self.pnd1_july.generate_report()
        self.pnd1_august.generate_report()
        self.pnd1_2021 = self.pnd1_year_obj.create(
            {
                "company_id": self.company_kaamelott.id,
                "year": 2021,
            }
        )
        self.pnd1_2021.generate_report()
        self.pnd1_2021.generate_withholding_tax_certificates()
        self.wtc_lancelot = self.wtc_obj.search(
            [("employee_id", "=", self.lancelot.id)]
        )

    def test_compute_tots(self):
        self.wtc_lancelot.line[4].amount_paid = 2000
        self.wtc_lancelot.line[5].amount_paid = 5000
        self.wtc_lancelot.line[4].tax_withheld = 1000
        self.wtc_lancelot.line[5].tax_withheld = 2000

        self.wtc_lancelot._compute_tot_income()
        self.wtc_lancelot._compute_tot_tax_paid()

        self.assertEqual(self.wtc_lancelot.tot_income, 13000)
        self.assertEqual(self.wtc_lancelot.tot_tax_paid, 3000)

    def test_fetch_duplicates(self):
        with self.assertRaises(ValidationError):
            self.wtc_obj.create(
                {
                    "year": 2021,
                    "company_id": self.company_kaamelott.id,
                    "employee_id": self.lancelot.id,
                }
            )
