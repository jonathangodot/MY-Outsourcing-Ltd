from odoo.tests.common import TransactionCase

from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestOTCommon(TransactionCase):
    @classmethod
    def setUpClass(self):
        super(TestOTCommon, self).setUpClass()
        self.employee_obj = self.env["hr.employee"]
        self.contract_obj = self.env["hr.contract"]
        self.structure_obj = self.env["hr.payroll.structure.type"]
        self.we_type_obj = self.env["hr.work.entry.type"]
        self.ot_obj = self.env["hr.overtime"]
        self.ot_need_obj = self.env["hr.overtime.need"]
        self.ot_schedule_obj = self.env["hr.overtime.schedule"]

        # Creating employees
        self.roi_lott = self.employee_obj.create(
            {
                "name": "Roi Lott",
            }
        )
        self.roi_burgonde = self.employee_obj.create(
            {
                "name": "Roi Burgonde",
            }
        )
        self.duc_daquitaine = self.employee_obj.create(
            {
                "name": "Duc D'Aquitaine",
            }
        )

        # Getting a work entry type to assign to the OTs
        self.we_ot = self.we_type_obj.search([("code", "=", "WORK300")], limit=1)

        # Creating a salary structure to create valid contracts
        self.table_ronde_structure = self.structure_obj.create(
            {
                "name": "Table Ronde",
                "wage_type": "monthly",
            }
        )

        # Creating contracts for the employees, and opening them
        self.contract_lott = self.contract_obj.create(
            {
                "name": "Contract Lott",
                "active": True,
                "employee_id": self.roi_lott.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 1000,
                "structure_type_id": self.table_ronde_structure.id,
                "state": "open",
            }
        )
        self.contract_burgonde = self.contract_obj.create(
            {
                "name": "Contract Burgonde",
                "active": True,
                "employee_id": self.roi_burgonde.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 1000,
                "structure_type_id": self.table_ronde_structure.id,
                "state": "open",
            }
        )
        self.contract_aquitaine = self.contract_obj.create(
            {
                "name": "Contract Aquitaine",
                "active": True,
                "employee_id": self.duc_daquitaine.id,
                "date_start": date(2017, 1, 1),
                "date_end": False,
                "wage": 1000,
                "structure_type_id": self.table_ronde_structure.id,
                "state": "open",
            }
        )

        # Creating empty schedules
        self.schedule_lott = self.ot_schedule_obj.create(
            {
                "employee_id": self.roi_lott.id,
            }
        )
        self.schedule_burgonde = self.ot_schedule_obj.create(
            {
                "employee_id": self.roi_burgonde.id,
            }
        )
        self.schedule_aquitaine = self.ot_schedule_obj.create(
            {
                "employee_id": self.duc_daquitaine.id,
            }
        )

        # Creating a few OTs
        self.ot_lott_1 = self.ot_obj.create(
            {
                "employee_id": self.roi_lott.id,
                "work_entry_type_id": self.we_ot.id,
                "date_start": datetime(2022, 8, 1, 18, 0, 0),
                "date_stop": datetime(2022, 8, 1, 20, 0, 0),
                "ot_schedule": self.schedule_lott.id,
            }
        )
        self.ot_lott_2 = self.ot_obj.create(
            {
                "employee_id": self.roi_lott.id,
                "work_entry_type_id": self.we_ot.id,
                "date_start": datetime(2022, 8, 2, 18, 0, 0),
                "date_stop": datetime(2022, 8, 2, 20, 0, 0),
                "ot_schedule": self.schedule_lott.id,
            }
        )
        self.ot_burgonde_1 = self.ot_obj.create(
            {
                "employee_id": self.roi_burgonde.id,
                "work_entry_type_id": self.we_ot.id,
                "date_start": datetime(2022, 8, 1, 18, 0, 0),
                "date_stop": datetime(2022, 8, 1, 20, 0, 0),
                "ot_schedule": self.schedule_burgonde.id,
            }
        )
        self.ot_burgonde_2 = self.ot_obj.create(
            {
                "employee_id": self.roi_burgonde.id,
                "work_entry_type_id": self.we_ot.id,
                "date_start": datetime(2022, 8, 2, 18, 0, 0),
                "date_stop": datetime(2022, 8, 2, 20, 0, 0),
                "ot_schedule": self.schedule_burgonde.id,
            }
        )

        # Create a need
        self.need = self.env["hr.overtime.need"].create(
            {
                "name": "Quete du Graal",
                "date_from": date(2022, 8, 1),
                "date_to": date.today() + timedelta(days=10),
                "hours_needed": 10,
                "state": "DRAFT",
            }
        )
