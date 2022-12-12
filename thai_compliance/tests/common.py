from odoo.tests.common import TransactionCase
import logging
from odoo.fields import Date
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class TestThaiComplianceCommon(TransactionCase):
    @classmethod
    def setUpClass(self):
        super(TestThaiComplianceCommon, self).setUpClass()
        self.employee_obj = self.env["hr.employee"]
        self.contract_obj = self.env["hr.contract"]
        self.payslip_obj = self.env["hr.payslip"]
        self.structure_obj = self.env["hr.payroll.structure"]
        self.schedule_obj = self.env["resource.calendar"]
        self.structure_type_obj = self.env["hr.payroll.structure.type"]
        self.company_obj = self.env["res.company"]
        self.common_obj = self.env["thailand.compliance.common.test"]
        self.salary_rule_obj = self.env["hr.salary.rule"]

        # Creating companies
        self.company_kaamelott = self.company_obj.create(
            {
                "name": "Royaume de Logre",
                "building": "Chateau de Kaamelott",
                "room_no": "1",
                "floor": "1",
                "street": "Graal Rd.",
                "street2": "Soi Excalibur",
                "address_no": "666",
                "address_moo": "6",
                "district": "Kaamelott",
                "city": "Logre",
                "province": "In The Forest",
                "zip": "66666",
                "country_id": 231,
                "pid": "1234567890123",
                "tin": "1234567890",
            }
        )
        self.company_aquitaine = self.company_obj.create(
            {
                "name": "Ducher d'Aquitaine",
                "building": "Chateau d'Aquitaine",
                "floor": "2",
                "address_no": "777",
                "address_moo": "7",
                "city": "Aquitaine",
                "province": "On the coast",
                "zip": "77777",
                "country_id": 75,
                "pid": "2345678901234",
                "tin": "2345678901",
                "parent_id": self.company_kaamelott.id,
                "branch_nb": 1,
            }
        )

        for company in self.env["res.company"].search([]):
            company.currency_id = self.env.ref("base.THB").id

        # Creating employees
        self.arthur = self.employee_obj.create(
            {"name": "Arthur", "company_id": self.company_kaamelott.id}
        )
        self.leodagan = self.employee_obj.create(
            {"name": "Leodagan", "company_id": self.company_kaamelott.id}
        )
        self.lancelot = self.employee_obj.create(
            {"name": "Lancelot", "company_id": self.company_kaamelott.id}
        )
        self.guenievre = self.employee_obj.create(
            {"name": "Guenievre", "company_id": self.company_kaamelott.id}
        )
        self.merlin = self.employee_obj.create(
            {"name": "Merlin", "company_id": self.company_kaamelott.id}
        )
        self.yvain = self.employee_obj.create(
            {"name": "Yvain", "company_id": self.company_kaamelott.id}
        )
        self.gauvain = self.employee_obj.create(
            {"name": "Gauvain", "company_id": self.company_aquitaine.id}
        )
        self.perceval = self.employee_obj.create(
            {"name": "Perceval", "company_id": self.company_aquitaine.id}
        )

        # Creating schedule
        self.schedule = self.schedule_obj.create({"name": "Schedule"})

        # Creating a salary structure to create valid contracts
        self.table_ronde_structure_type = self.structure_type_obj.create(
            {
                "name": "Table Ronde",
                "wage_type": "monthly",
                "count_in_pnd1": True,
                "count_in_sps1_10": True,
            }
        )
        self.table_ronde_structure = self.structure_obj.create(
            {
                "name": "Table Ronde",
                "type_id": self.table_ronde_structure_type.id,
            }
        )
        self.orcanie_structure_type = self.structure_type_obj.create(
            {"name": "Orcanie", "wage_type": "monthly"}
        )
        self.orcanie_structure = self.structure_obj.create(
            {
                "name": "Orcanie",
                "type_id": self.orcanie_structure_type.id,
            }
        )

        # Creating contracts for the employees, and opening them
        self.contract_arthur = self.contract_obj.create(
            {
                "name": "Contract Arthur",
                "active": True,
                "employee_id": self.arthur.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 1000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_leodagan = self.contract_obj.create(
            {
                "name": "Contract Leodagan",
                "active": True,
                "employee_id": self.leodagan.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 2000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_lancelot = self.contract_obj.create(
            {
                "name": "Contract Lancelot",
                "active": True,
                "employee_id": self.lancelot.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 3000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_guenievre = self.contract_obj.create(
            {
                "name": "Contract Guenievre",
                "active": True,
                "employee_id": self.guenievre.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 4000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_merlin = self.contract_obj.create(
            {
                "name": "Contract Merlin",
                "active": True,
                "employee_id": self.merlin.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 5000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_yvain = self.contract_obj.create(
            {
                "name": "Contract Yvain",
                "active": True,
                "employee_id": self.yvain.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 6000,
                "structure_type_id": self.table_ronde_structure_type.id,
                "state": "open",
            }
        )
        self.contract_gauvain = self.contract_obj.create(
            {
                "name": "Contract Gauvain",
                "active": True,
                "employee_id": self.gauvain.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 7000,
                "hourly_wage": 100,
                "structure_type_id": self.orcanie_structure_type.id,
                "state": "open",
            }
        )
        self.contract_perceval = self.contract_obj.create(
            {
                "name": "Contract Perceval",
                "active": True,
                "employee_id": self.perceval.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 8000,
                "hourly_wage": 200,
                "structure_type_id": self.orcanie_structure_type.id,
            }
        )

        self.secu_rule = self.salary_rule_obj.create(
            {
                "name": "Secu",
                "code": "SS",
                "category_id": self.env["hr.salary.rule.category"]
                .search([("code", "=", "DED")])
                .id,
                "struct_id": self.table_ronde_structure.id,
                "sequence": 99,
                "condition_select": "none",
                "amount_select": "fix",
                "quantity": 1,
                "amount_fix": 100,
            }
        )

        self.common_doc_kaamelott = self.common_obj.create(
            {"company_id": self.company_kaamelott.id, "year": 2021}
        )
        self.common_doc_aquitaine = self.common_obj.create(
            {"company_id": self.company_aquitaine.id}
        )
        self.test_employees = [
            self.arthur,
            self.leodagan,
            self.lancelot,
            self.guenievre,
            self.merlin,
            self.yvain,
            self.gauvain,
        ]
        for employee in self.test_employees:
            self.generate_payslip(employee)

    @classmethod
    def generate_payslip(self, employee):
        _logger.info(f"Creating payslip for employee {employee.name}")
        self.env.company = employee.company_id
        employee.generate_work_entries(
            date_start=Date.to_date("2020-01-01"), date_stop=datetime.today()
        )
        payslip_run = self.env["hr.payslip.run"].create(
            {
                "date_start": Date.to_date("2021-07-01"),
                "date_end": Date.to_date("2021-07-31"),
                "name": "Batch Test",
                "company_id": self.company_kaamelott.id,
            }
        )
        # I create record for generating the payslip for this Payslip run.
        payslip_employee = self.env["hr.payslip.employees"].create(
            {
                "employee_ids": [(4, employee.id)],
                "structure_id": employee.contract_id.structure_type_id.struct_ids[0].id,
            }
        )
        # I generate the payslip by clicking on Generat button wizard.
        payslip_employee.with_context(active_id=payslip_run.id).compute_sheet()
        payslip_run = self.env["hr.payslip.run"].create(
            {
                "date_start": Date.to_date("2021-08-01"),
                "date_end": Date.to_date("2021-08-31"),
                "name": "Batch Test",
                "company_id": self.company_kaamelott.id,
            }
        )
        # I create record for generating the payslip for this Payslip run.
        payslip_employee = self.env["hr.payslip.employees"].create(
            {
                "employee_ids": [(4, employee.id)],
                "structure_id": employee.contract_id.structure_type_id.struct_ids[0].id,
            }
        )
        # I generate the payslip by clicking on Generat button wizard.
        payslip_employee.with_context(
            active_id=payslip_run.id, company_id=self.company_kaamelott.id
        ).compute_sheet()

        slips = self.payslip_obj.search([("employee_id", "=", employee.id)])
        for slip in slips:
            slip.company_id = employee.company_id.id
            slip.state = "done"
