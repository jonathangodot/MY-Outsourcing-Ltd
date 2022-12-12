from odoo.tests import tagged
from odoo.fields import Date
from .common import TestThaiCompliancePayrollCommon
from ..utils.const import *
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_payroll_common", "newlogic", "thai_compliance")
class TestThaiComplianceCommon(TestThaiCompliancePayrollCommon):
    @classmethod
    def setUpClass(self):
        super(TestThaiComplianceCommon, self).setUpClass()

    def test_count_payslip_line(self):
        self.assertEqual(
            self.pnd1_july.count_payslip_line(self.arthur, "code_gross"),
            1000,
            "Payslip line total should be computed correctly",
        )

    def test_count_payslip_line_with_previous_company(self):
        this_year = date.today().year
        calogrenant = self.employee_obj.create(
            {
                "name": "Calogrenant",
            }
        )
        calogrenant_contract = self.contract_obj.create(
            {
                "name": "Calogrenant Contract",
                "active": True,
                "employee_id": calogrenant.id,
                "wage": 2000,
                "date_start": f"{this_year}-03-01",
                "state": "open",
                "structure_type_id": self.table_ronde_structure_type.id,
                "company_id": self.company_kaamelott.id,
            }
        )
        calogrenant.worked_before = "EMPLOYED"
        calogrenant.previous_revenue = 5000
        self.env.company = calogrenant.company_id
        self.create_payslip(this_year, calogrenant)
        self.pnd1_july.year = this_year

        self.assertEqual(
            self.pnd1_july.count_payslip_line(
                calogrenant,
                "code_gross",
                report_is_for_employee=True,
                previous_company_amount_attribute="previous_revenue",
            ),
            7000,
            "Payslip line total should be computed correctly",
        )

    def create_payslip(self, year, calogrenant):
        calogrenant.generate_work_entries(
            date_start=Date.to_date("2020-01-01"), date_stop=datetime.today()
        )
        payslip_run = self.env["hr.payslip.run"].create(
            {
                "date_start": Date.to_date(f"{year}-07-01"),
                "date_end": Date.to_date(f"{year}-07-31"),
                "name": "Batch Test",
                "company_id": self.company_kaamelott.id,
            }
        )
        # I create record for generating the payslip for this Payslip run.
        payslip_employee = self.env["hr.payslip.employees"].create(
            {
                "employee_ids": [(4, calogrenant.id)],
                "structure_id": calogrenant.contract_id.structure_type_id.struct_ids[
                    0
                ].id,
            }
        )
        # I generate the payslip by clicking on Generat button wizard.
        payslip_employee.with_context(active_id=payslip_run.id).compute_sheet()
        payslip_run = self.env["hr.payslip.run"].create(
            {
                "date_start": Date.to_date(f"{year}-08-01"),
                "date_end": Date.to_date(f"{year}-08-31"),
                "name": "Batch Test",
                "company_id": self.company_kaamelott.id,
            }
        )
        # I create record for generating the payslip for this Payslip run.
        payslip_employee = self.env["hr.payslip.employees"].create(
            {
                "employee_ids": [(4, calogrenant.id)],
                "structure_id": calogrenant.contract_id.structure_type_id.struct_ids[
                    0
                ].id,
            }
        )
        # I generate the payslip by clicking on Generat button wizard.
        payslip_employee.with_context(active_id=payslip_run.id).compute_sheet()

        slips = self.payslip_obj.search([("employee_id", "=", calogrenant.id)])
        for slip in slips:
            slip.company_id = calogrenant.company_id.id

    def test_code_settings(self):
        self.assertEqual(
            self.pnd1_july.code_settings(),
            {"code_gross": "GROSS", "code_tax": "PT", "code_secu": "SS"},
            "Code settings should be correct",
        )
