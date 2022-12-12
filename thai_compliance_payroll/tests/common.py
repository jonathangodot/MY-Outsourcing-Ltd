from ...thai_compliance.tests.common import TestThaiComplianceCommon
from datetime import date


class TestThaiCompliancePayrollCommon(TestThaiComplianceCommon):
    @classmethod
    def setUpClass(self):
        super(TestThaiCompliancePayrollCommon, self).setUpClass()

        self.payroll_report_field_obj = self.env["hr.payroll.report.income.type"]
        self.config_obj = self.env["res.config.settings"]

        self.gross_set = self.config_obj.create({"code_gross": "GROSS"})
        self.tax_set = self.config_obj.create({"code_tax": "PT"})
        self.secu_set = self.config_obj.create({"code_secu": "SS"})
        self.gross_set.set_values()
        self.tax_set.set_values()
        self.secu_set.set_values()

        self.orcanie_structure_type.tax_3_percent = True

        for employee in self.test_employees:
            slips = self.payslip_obj.search([("employee_id", "=", employee.id)])
            [slip.compute_sheet() for slip in slips]

        self.calogrenant = self.employee_obj.create(
            {"name": "Calogrenan", "company_id": self.company_kaamelott.id}
        )
        self.elias = self.employee_obj.create(
            {"name": "Elias", "company_id": self.company_kaamelott.id}
        )
        self.test_employees += self.calogrenant + self.elias
        self.contract_calogrenant = self.contract_obj.create(
            {
                "name": "Contract Calogrenant",
                "active": True,
                "employee_id": self.calogrenant.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 8000,
                "hourly_wage": 200,
                "structure_type_id": self.orcanie_structure_type.id,
                "state": "open",
            }
        )
        self.contract_elias = self.contract_obj.create(
            {
                "name": "Contract Elias",
                "active": True,
                "employee_id": self.elias.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 9000,
                "hourly_wage": 300,
                "structure_type_id": self.orcanie_structure_type.id,
                "state": "open",
            }
        )
        self.generate_payslip(self.calogrenant)
        self.generate_payslip(self.elias)

        self.pnd1_month_obj = self.env["thailand.pnd1.month"]
        self.pnd1_detail_obj = self.env["thailand.pnd1.month.line"]
        self.pnd1_year_obj = self.env["thailand.pnd1.year.company"]
        self.pnd1_july = self.pnd1_month_obj.create(
            {
                "year": 2021,
                "month": "7",
                "company_id": self.company_kaamelott.id,
            }
        )
        self.pnd1_august = self.pnd1_month_obj.create(
            {
                "year": 2021,
                "month": "8",
                "company_id": self.company_kaamelott.id,
            }
        )
