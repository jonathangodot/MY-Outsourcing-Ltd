from odoo.tests import tagged
from odoo.exceptions import UserError

from .common import TestWithholdingTaxThailand
from ..models import hr_payslip

import logging

_logger = logging.getLogger(__name__)


@tagged("payslip_thailand", "newlogic")
class TestHrPayslip(TestWithholdingTaxThailand):
    """
    TODO : adapt tests to daily wages
    """

    @classmethod
    def setUpClass(self):
        super(TestHrPayslip, self).setUpClass()

    def test_compute_witholding_tax_correct(self):
        arthur_taxes = hr_payslip.compute_withholding_taxes_thailand(
            self.arthur, self.arthur_payslips[-1], self.arthur_categories
        )

        lancelot_taxes = hr_payslip.compute_withholding_taxes_thailand(
            self.lancelot, self.lancelot_payslips[-1], self.lancelot_categories
        )

        leodagan_taxes = hr_payslip.compute_withholding_taxes_thailand(
            self.leodagan, self.leodagan_payslips[-1], self.leodagan_categories
        )

        perceval_taxes = hr_payslip.compute_withholding_taxes_thailand(
            self.perceval, self.perceval_payslips[-1], self.perceval_categories
        )

        expected_arthur_taxes = 2775
        expected_lancelot_taxes = 10600
        expected_leodagan_taxes = 0
        expected_perceval_taxes = 23600

        self.assertEqual(arthur_taxes, expected_arthur_taxes)
        self.assertEqual(lancelot_taxes, expected_lancelot_taxes)
        self.assertEqual(leodagan_taxes, expected_leodagan_taxes)
        self.assertEqual(perceval_taxes, expected_perceval_taxes)

    def test_compute_income_tax_correct_values(self):
        test_case1 = hr_payslip.compute_income_tax(500000)
        test_case2 = hr_payslip.compute_income_tax(1160000)
        test_case3 = hr_payslip.compute_income_tax(7040000)

        expected_value1 = 27500.0
        expected_value2 = 155000.0
        expected_value3 = 1979000.0

        assert test_case1 == expected_value1
        assert test_case2 == expected_value2
        assert test_case3 == expected_value3

    def test_compute_income_tax_input_string(self):
        try:
            test_case = hr_payslip.compute_income_tax("a")
        except TypeError:
            assert True

    def test_compute_income_tax_negative_input(self):
        try:
            test_case = hr_payslip.compute_income_tax(-1)
        except UserError:
            assert True

    """TODO : Complete test suite"""
