from odoo.tests.common import TransactionCase

from ..models import hr_payslip

from datetime import date
import logging

_logger = logging.getLogger(__name__)


class TestWithholdingTaxThailand(TransactionCase):
    @classmethod
    def setUpClass(self):
        """
        Test context :
        The tests took place in september

        Arthur :
        Works in the company for a few years. He just got a raise, from 50,000THB a month to 70,000THB a month.

        Lancelot :
        Has a pre determined contract. He worked from June, and his contract expires in November.
        This contact assure him a salary of 100,000THB a month.

        Leodagan :
        Has just been hired, this month will be his first salary of 60,000THB a month.

        Perceval :
        Has been working in the company for a long time. But he just quit, and this month he will
        get his last salary of 80,000THB a month.


        ################
        #### TODO : REFACTORISER
        ################
        """
        super(TestWithholdingTaxThailand, self).setUpClass()

        TESTING_MONTH = 9
        TESTING_YEAR = 2021

        def create_employee(
            name,
            expenses,
            personal_allowance,
            spouse_allowance,
            parents_allowance,
            children_before_2018,
            children_since_2018,
            insurance_premium,
            provident_fund,
            housing_loan,
            provident_fund_retirement_mutual_fund,
            ssf,
            donations,
        ):
            employee_instance = self.env["hr.employee"].create(
                {
                    "name": name,
                    "expenses": expenses,
                    "personal_allowance": personal_allowance,
                    "spouse_allowance": spouse_allowance,
                    "parents_allowance": parents_allowance,
                    "children_before_2018": children_before_2018,
                    "children_since_2018": children_since_2018,
                    "insurance_premium": insurance_premium,
                    "provident_fund": provident_fund,
                    "housing_loan": housing_loan,
                    "provident_fund_retirement_mutual_fund": provident_fund_retirement_mutual_fund,
                    "ssf": ssf,
                    "donations": donations,
                }
            )
            return employee_instance

        def create_payslip(
            name,
            employee_id,
            contract_id,
            date_from,
            date_to,
            sum_worked_hours,
            normal_wage,
            state="draft",
        ):
            payslip_instance = self.env["hr.payslip"].create(
                {
                    "name": name,
                    "employee_id": employee_id,
                    "contract_id": contract_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "sum_worked_hours": sum_worked_hours,
                    "normal_wage": normal_wage,
                    "state": state,
                }
            )
            payslip_instance.action_refresh_from_work_entries()
            payslip_instance.action_payslip_done()
            return payslip_instance

        def create_contract(name, active, employee_id, date_start, wage, date_end=None):
            contract_instance = self.env["hr.contract"].create(
                {
                    "name": name,
                    "active": active,
                    "employee_id": employee_id,
                    "date_start": date_start,
                    "date_end": date_end,
                    "wage": wage,
                    "structure_type_id": self.env["hr.payroll.structure.type"]
                    .search([("name", "=", "Worker")])
                    .id,
                    "resource_calendar_id": self.env["resource.calendar"]
                    .search([])[0]
                    .id,
                }
            )
            return contract_instance

        def create_line(
            name,
            code,
            slip_id,
            salary_rule_id,
            employee_id,
            contract,
            rate,
            amount,
            quantity,
            total,
            date_from,
            date_to,
        ):
            line_instance = self.env["hr.payslip.line"].create(
                {
                    "name": name,
                    "code": code,
                    "slip_id": slip_id,
                    "salary_rule_id": salary_rule_id,
                    "employee_id": employee_id,
                    "contract_id": contract.id,
                    "rate": rate,
                    "amount": amount,
                    "quantity": quantity,
                    "total": total,
                    "date_from": date_from,
                    "date_to": date_to,
                }
            )
            return line_instance

        def create_payslips(employee, contract, sum_worked_hours):
            payslips = [
                create_payslip(
                    name=f"{employee.name}_payslip_{str(i)}",
                    employee_id=employee.id,
                    contract_id=contract.id,
                    date_from=date(2021, i, 1),
                    date_to=date(
                        2021,
                        i,
                        (
                            28
                            if i == 2
                            else (31 if i in [1, 3, 5, 7, 8, 10, 12] else 30)
                        ),
                    ),
                    sum_worked_hours=sum_worked_hours,
                    normal_wage=contract.wage,
                )
                for i in range(
                    (
                        contract.date_start.month
                        if contract.date_start.year == TESTING_YEAR
                        else 1
                    ),
                    (contract.date_end.month if contract.date_end else TESTING_MONTH)
                    + 1,
                )
            ]
            return payslips

        self.withholding_thailand_rule = self.env["hr.salary.rule"].create(
            {
                "name": "Whithholding Thailand",
                "code": "PP",
                "struct_id": 1,
                "sequence": 1000,
                "quantity": 1,
                "category_id": 4,
                "active": True,
                "appears_on_payslip": True,
                "condition_select": "none",
                "condition_range": "contract.wage",
                "condition_python": "",
                "amount_select": "code",
                "amount_python_compute": "result = compute_withholding_taxes_thailand(employee, payslip, categories)",
            }
        )

        """
        Create employees
        """
        self.arthur = create_employee(
            name="Arthur",
            expenses=True,
            personal_allowance=True,
            spouse_allowance=True,
            parents_allowance=2,
            children_before_2018=0,
            children_since_2018=0,
            insurance_premium=10000,
            provident_fund=0,
            housing_loan=10000,
            provident_fund_retirement_mutual_fund=0,
            ssf=0,
            donations=15000,
        )

        self.lancelot = create_employee(
            name="Lancelot",
            expenses=True,
            personal_allowance=True,
            spouse_allowance=False,
            parents_allowance=0,
            children_before_2018=0,
            children_since_2018=0,
            insurance_premium=0,
            provident_fund=0,
            housing_loan=0,
            provident_fund_retirement_mutual_fund=0,
            ssf=0,
            donations=0,
        )

        self.leodagan = create_employee(
            name="Leodagan",
            expenses=True,
            personal_allowance=True,
            spouse_allowance=True,
            parents_allowance=1,
            children_before_2018=2,
            children_since_2018=0,
            insurance_premium=15000,
            provident_fund=0,
            housing_loan=45000,
            provident_fund_retirement_mutual_fund=0,
            ssf=0,
            donations=50000,
        )

        self.perceval = create_employee(
            name="Perceval",
            expenses=True,
            personal_allowance=True,
            spouse_allowance=False,
            parents_allowance=1,
            children_before_2018=1,
            children_since_2018=0,
            insurance_premium=0,
            provident_fund=0,
            housing_loan=0,
            provident_fund_retirement_mutual_fund=0,
            ssf=0,
            donations=30000,
        )

        """
        ################################
        ################################
        #############   Arthur

        Contracts :
        Arthur has 2 types of contract because he had a raise this month.
        
        TODO : Refacto, and clean the code
        """

        self.arthur_contract_1 = create_contract(
            f"{self.arthur.name}_contract_1",
            active=False,
            employee_id=self.arthur.id,
            date_start=date(2019, 5, 9),
            date_end=date(2021, 8, 31),
            wage=50000,
        )
        self.arthur_contract_2 = create_contract(
            f"{self.arthur.name}_contract_2",
            active=True,
            employee_id=self.arthur.id,
            date_start=date(2021, 9, 1),
            wage=65000,
        )
        self.arthur_contracts = [self.arthur_contract_1, self.arthur_contract_2]

        """
        Creats all the payslips regarding all of Arthur's contracts
        """
        self.arthur_payslips = []
        for contract in self.arthur_contracts:
            _logger.info(f"Creating contract for {contract.name}")
            self.arthur_payslips += create_payslips(self.arthur, contract, 160)
        _logger.info("\n\n\n")
        for slip in self.arthur_payslips:
            _logger.info(
                f"slip {slip.name} : {slip.date_from} - {slip.date_to}, employee : {slip.employee_id.name}, contract : {slip.contract_id.name}, worked hours : {slip.sum_worked_hours}, normal wage : {slip.normal_wage}"
            )
        _logger.info("\n\n\n")

        """
        This 'categories' object is the one related to the last payslip.
        It is used in the test_hr_payslip.py file.
        """
        self.arthur_categories = self.arthur_payslips[-1]._get_localdict()["categories"]
        self.arthur_categories.GROSS = self.arthur_payslips[-1].normal_wage
        self.arthur_categories.BASIC = self.arthur_payslips[-1].normal_wage

        """
        A line is a line in the payslip. The interesting lines are the gross salary, and the withholding tax.
        """
        self.arthur_lines = []
        for slip in self.arthur_payslips:
            """
            Creates the 'categories' object needed to compute the paid taxes for this particular payslip
            """
            categories = slip._get_localdict()["categories"]
            categories.GROSS, categories.BASIC = slip.normal_wage, slip.normal_wage
            slip.compute_sheet()

            """
            Creates the gross salary line for this paylip.
            Note that the gross salary is equal to the normal_wage of the slip, wich is the wage writen in the
            contract. For the testing od this module, this is sufficient, as the purpose of it is to compute the 
            withholding tax from the gross. Therefore, the tests can ignore the other lines usually present in
            a payslip.
            """
            self.arthur_lines.append(
                create_line(
                    name="Gross",
                    code="GROSS",
                    slip_id=slip.id,
                    salary_rule_id=2,
                    employee_id=self.arthur.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=slip.normal_wage,
                    quantity=1,
                    total=slip.normal_wage,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

            """
            Calculate the taxes paid this month
            """
            compute_tax = hr_payslip.compute_withholding_taxes_thailand(
                self.arthur, slip, categories
            )
            if (
                slip.contract_id.name == "Arthur_contract_1"
                and slip.date_from.month == TESTING_MONTH
            ):
                """Ending a contract"""
                slip.contract_id.date_end = date(2021, 8, 31)

            """
            Create the line containing the taxes paid this month. It is important to calculate the taxes already
            paid, and deduce the taxes left to pay.
            """
            self.arthur_lines.append(
                create_line(
                    name="Withholding",
                    code="PP",
                    slip_id=slip.id,
                    salary_rule_id=self.withholding_thailand_rule.id,
                    employee_id=self.arthur.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=compute_tax,
                    quantity=1,
                    total=compute_tax,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

        """
        Lancelot's payslips
        """
        self.lancelot_contract = create_contract(
            f"{self.lancelot.name}_contract",
            active=True,
            employee_id=self.lancelot.id,
            date_start=date(2021, 6, 1),
            date_end=date(2021, 10, 31),
            wage=100000,
        )

        self.lancelot_payslips = create_payslips(
            self.lancelot, self.lancelot_contract, 160
        )

        self.lancelot_categories = self.lancelot_payslips[-1]._get_localdict()[
            "categories"
        ]
        self.lancelot_categories.GROSS = self.lancelot_payslips[-1].normal_wage
        self.lancelot_categories.BASIC = self.lancelot_payslips[-1].normal_wage

        self.lancelot_lines = []
        for slip in self.lancelot_payslips:
            categories = slip._get_localdict()["categories"]
            categories.GROSS, categories.BASIC = slip.normal_wage, slip.normal_wage
            slip.compute_sheet()

            self.lancelot_lines.append(
                create_line(
                    name="Gross",
                    code="GROSS",
                    slip_id=slip.id,
                    salary_rule_id=2,
                    employee_id=self.lancelot.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=slip.normal_wage,
                    quantity=1,
                    total=slip.normal_wage,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

            compute_tax = hr_payslip.compute_withholding_taxes_thailand(
                self.lancelot, slip, categories
            )

            self.lancelot_lines.append(
                create_line(
                    name="Withholding",
                    code="PP",
                    slip_id=slip.id,
                    salary_rule_id=self.withholding_thailand_rule.id,
                    employee_id=self.lancelot.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=compute_tax,
                    quantity=1,
                    total=compute_tax,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

        """
        Leodagan's payslips
        """
        self.leodagan_contract = create_contract(
            f"{self.leodagan.name}_contract",
            active=True,
            employee_id=self.leodagan.id,
            date_start=date(2021, 9, 1),
            wage=60000,
        )

        self.leodagan_payslips = create_payslips(
            self.leodagan, self.leodagan_contract, 160
        )

        self.leodagan_categories = self.leodagan_payslips[-1]._get_localdict()[
            "categories"
        ]
        self.leodagan_categories.GROSS = self.leodagan_payslips[-1].normal_wage
        self.leodagan_categories.BASIC = self.leodagan_payslips[-1].normal_wage

        self.leodagan_lines = []
        for slip in self.leodagan_payslips:
            categories = slip._get_localdict()["categories"]
            categories.GROSS, categories.BASIC = slip.normal_wage, slip.normal_wage
            slip.compute_sheet()

            self.leodagan_lines.append(
                create_line(
                    name="Gross",
                    code="GROSS",
                    slip_id=slip.id,
                    salary_rule_id=2,
                    employee_id=self.leodagan.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=slip.normal_wage,
                    quantity=1,
                    total=slip.normal_wage,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

            compute_tax = hr_payslip.compute_withholding_taxes_thailand(
                self.leodagan, slip, categories
            )

            self.leodagan_lines.append(
                create_line(
                    name="Withholding",
                    code="PP",
                    slip_id=slip.id,
                    salary_rule_id=self.withholding_thailand_rule.id,
                    employee_id=self.leodagan.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=compute_tax,
                    quantity=1,
                    total=compute_tax,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

        """
        Perceval's payslips
        """
        self.perceval_contract = create_contract(
            f"{self.perceval.name}_contract",
            active=True,
            employee_id=self.perceval.id,
            date_start=date(2015, 2, 1),
            wage=80000,
        )

        self.perceval_payslips = create_payslips(
            self.perceval, self.perceval_contract, 160
        )

        self.perceval_categories = self.perceval_payslips[-1]._get_localdict()[
            "categories"
        ]
        self.perceval_categories.GROSS = self.perceval_payslips[-1].normal_wage
        self.perceval_categories.BASIC = self.perceval_payslips[-1].normal_wage

        self.perceval_lines = []
        for slip in self.perceval_payslips:
            if slip.date_from.month == TESTING_MONTH:
                slip.contract_id.date_end = date(2021, 9, 30)

            categories = slip._get_localdict()["categories"]
            categories.GROSS, categories.BASIC = slip.normal_wage, slip.normal_wage
            slip.compute_sheet()

            self.perceval_lines.append(
                create_line(
                    name="Gross",
                    code="GROSS",
                    slip_id=slip.id,
                    salary_rule_id=2,
                    employee_id=self.perceval.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=slip.normal_wage,
                    quantity=1,
                    total=slip.normal_wage,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )

            compute_tax = hr_payslip.compute_withholding_taxes_thailand(
                self.perceval, slip, categories
            )

            self.perceval_lines.append(
                create_line(
                    name="Withholding",
                    code="PP",
                    slip_id=slip.id,
                    salary_rule_id=self.withholding_thailand_rule.id,
                    employee_id=self.perceval.id,
                    contract=slip.contract_id,
                    rate=100.0,
                    amount=compute_tax,
                    quantity=1,
                    total=compute_tax,
                    date_from=slip.date_from,
                    date_to=slip.date_to,
                )
            )
