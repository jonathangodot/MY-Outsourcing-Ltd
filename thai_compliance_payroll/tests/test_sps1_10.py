from odoo.tests import tagged
from .common import TestThaiCompliancePayrollCommon
from ..utils.const import *
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_payroll_sps1_10", "newlogic", "thai_compliance")
class TestThailandSPS1_10(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestThailandSPS1_10, self).setUpClass()
        self.sps_obj = self.env["thailand.sps1.10"]
        self.sps_line_obj = self.env["thailand.sps1.10.branch.report"]
        self.sps1_10 = self.sps_obj.create(
            {"year": "2021", "month": "7", "company_id": self.company_kaamelott.id}
        )

    def test_generate_report(self):
        self.sps1_10.generate_report()
        self.assertEqual(
            self.sps1_10.year_be,
            "2564",
            "Year BE should be computed correctly",
        )
        self.assertEqual(self.sps1_10.employee_contrib, -600)
        self.assertEqual(self.sps1_10.employer_contrib, -600)
        self.assertEqual(self.sps1_10.total_contrib, -1200)
        self.assertEqual(self.sps1_10.total_wages, 38000)
        self.assertEqual(len(self.sps1_10.branch_report), 8)

        line = self.sps_line_obj.search(
            [
                ("sps1_10_id", "=", self.sps1_10.id),
                ("employee_id", "=", self.leodagan.id),
            ]
        )
        self.assertEqual(len(line), 1)
        self.assertEqual(line.actual_wages, 2000)
        self.assertEqual(line.contribution, -100)
