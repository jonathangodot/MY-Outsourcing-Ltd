from .common import TestOTCommon
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


@tagged("ot", "newlogic")
class TestOTNeed(TestOTCommon):
    @classmethod
    def setUpClass(self):
        super(TestOTNeed, self).setUpClass()

    def test_need_methods(self):
        # Make sur the need has been properly created
        self.assertEqual(self.need.name, "Quete du Graal")
        self.assertEqual(self.need.date_from, date(2022, 8, 1))
        self.assertEqual(self.need.date_to, date.today() + timedelta(days=10))
        self.assertEqual(self.need.hours_needed, 10)
        self.assertEqual(self.need.state, "DRAFT")

        # Test the confirm method
        self.need.set_to_validated()
        self.assertEqual(self.need.state, "VALIDATED")

        # Test the over method
        self.need.set_to_over()
        self.assertEqual(self.need.state, "OVER")

        # Test the draft method
        self.need.set_to_draft()
        self.assertEqual(self.need.state, "DRAFT")

        # Assign a schedule to the need
        self.need.ot_schedules = self.schedule_lott

        # Test that a need with a schedule does not raise an error
        self.need.count_hours()
        self.assertEqual(self.need.hours_filled, 0)
        self.assertEqual(self.need.percentage_filled, 0)

        # Test that the hours of an accepted schedule are counted
        self.schedule_lott.set_to_accepted()
        self.need.count_hours()
        self.assertEqual(self.need.hours_filled, 4)
        self.assertEqual(self.need.percentage_filled, 40)

        # Test that OTs scheduled after the end date of the need raise an error
        with self.assertRaises(ValidationError):
            self.ot_lott_3 = self.ot_obj.create(
                {
                    "employee_id": self.roi_lott.id,
                    "work_entry_type_id": self.we_ot.id,
                    "date_start": (datetime.now() + timedelta(days=20)).replace(
                        hour=18, minute=0, second=0
                    ),
                    "date_stop": (datetime.now() + timedelta(days=20)).replace(
                        hour=20, minute=0, second=0
                    ),
                    "ot_schedule": self.schedule_lott.id,
                }
            )
        # Test that OTs scheduled before the start date of the need raise an error
        with self.assertRaises(UserError):
            self.ot_lott_4 = self.ot_obj.create(
                {
                    "employee_id": self.roi_lott.id,
                    "work_entry_type_id": self.we_ot.id,
                    "date_start": datetime(2022, 1, 2, 18, 0, 0),
                    "date_stop": datetime(2022, 1, 2, 20, 0, 0),
                    "ot_schedule": self.schedule_lott.id,
                }
            )
            self.need.check_no_ot_before()

        # Test that a need with a end date before today is not over
        self.need.check_over()
        self.assertEqual(self.need.state, "DRAFT")

        # Test that publishing work entries for OTs in draft won't create work entries
        self.need.publish_all_work_entries()
        lott_we = self.env["hr.work.entry"].search(
            [("employee_id", "=", self.roi_lott.id)]
        )
        self.assertEqual(len(lott_we), 0)

        # Test that publishing work entries for OTs in validated state will create work entries
        for schedule in self.need.ot_schedules:
            schedule.set_to_accepted()
        self.need.publish_all_work_entries()
        lott_we = self.env["hr.work.entry"].search(
            [("employee_id", "=", self.roi_lott.id)]
        )
        self.assertEqual(len(lott_we), 2)

        # Test that a need with a date stop before today is over
        self.need.date_to = date.today() + timedelta(days=-1)
        self.need.check_over()
        self.assertEqual(self.need.state, "OVER")
