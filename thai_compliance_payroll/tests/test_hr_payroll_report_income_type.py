from odoo.tests import tagged
from .common import TestThaiCompliancePayrollCommon
from ..utils.const import *
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_report_income", "newlogic", "thai_compliance")
class TestHrPayrollReportIncomeType(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestHrPayrollReportIncomeType, self).setUpClass()

    def test_compute_model_field_name(self):
        self.assertEqual(
            self.payroll_report_field_obj.compute_model_field_name("test1"),
            "x_test1",
            "Model field name should be computed correctly",
        )
        self.assertEqual(
            self.payroll_report_field_obj.compute_model_field_name("Test 2"),
            "x_test_2",
            "Model field name should be computed correctly",
        )

    def test_crud_field(self):
        def get_field():
            field = self.env["ir.model.fields"].search(
                [
                    (
                        "name",
                        "=",
                        "x_test_3",
                    ),
                ]
            )

            return field

        field_name = "Test 3"
        field_model_name = self.payroll_report_field_obj.compute_model_field_name(
            field_name
        )
        model_name = "thailand.pnd1.month"
        self.payroll_report_field_obj.add_field_in_model(field_model_name, model_name)
        field = get_field()
        self.assertEqual(field.name, "x_test_3", "Field should be created in model")
        self.assertEqual(field.model, model_name, "Field should be created in model")
        self.assertEqual(field.field_description, "Test 3", "Field should be created")

        self.payroll_report_field_obj.remove_field_from_model(field_name, model_name)
        self.payroll_report_field_obj.search(
            [("name", "=", field_name)]
        ).remove_field_from_model(field_model_name, model_name)
        field = get_field()
        self.assertEqual(len(field), 0, "Field should be deleted in model")
