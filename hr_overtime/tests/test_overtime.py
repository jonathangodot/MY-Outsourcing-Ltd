from .common import TestOTCommon
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


@tagged("ot", "newlogic")
class TestOT(TestOTCommon):
    @classmethod
    def setUpClass(self):
        super(TestOT, self).setUpClass()

    def test_ot_methods(self):
        # Testing the repeat methods
        self.ot_lott_2.repeat_next_day()
        new_ot = self.ot_obj.search(
            [
                ("employee_id", "=", self.roi_lott.id),
                ("date_start", "=", datetime(2022, 8, 3, 18, 0, 0)),
                ("date_stop", "=", datetime(2022, 8, 3, 20, 0, 0)),
            ]
        )
        self.assertEqual(len(new_ot), 1)
        self.ot_lott_2.repeat_next_week()
        new_ot = self.ot_obj.search(
            [
                ("employee_id", "=", self.roi_lott.id),
                ("date_start", "=", datetime(2022, 8, 9, 18, 0, 0)),
                ("date_stop", "=", datetime(2022, 8, 9, 20, 0, 0)),
            ]
        )
        # Repeating a second time the same attendance creates an overlapping error
        self.assertEqual(len(new_ot), 1)
        with self.assertRaises(ValidationError):
            self.ot_lott_2.repeat_next_day()

        # Creating an OT before the start of the need creates an error
        with self.assertRaises(ValidationError):
            self.ot_lott_2.date_start = datetime(2015, 8, 3, 18, 0, 0)

        # Creating an OT with a end date before the start date creates an error
        with self.assertRaises(ValidationError):
            self.ot_lott_2.date_start = datetime(2022, 8, 3, 20, 0, 0)
            self.ot_lott_2.date_stop = datetime(2022, 8, 3, 18, 0, 0)

        # Creating an OT that overlapps with another OT creates an error
        with self.assertRaises(ValidationError):
            self.ot_obj.create(
                {
                    "employee_id": self.roi_lott.id,
                    "work_entry_type_id": self.we_ot.id,
                    "date_start": datetime(2022, 8, 3, 19, 0, 0),
                    "date_stop": datetime(2022, 8, 3, 21, 0, 0),
                    "ot_schedule": self.schedule_lott.id,
                }
            )

        # Check the cancel methods
        self.ot_lott_1.cancel()
        self.assertEqual(self.ot_lott_1.cancelled, "Y")
        self.ot_lott_1.revert_cancel()
        self.assertEqual(self.ot_lott_1.cancelled, "N")

    def test_publish_cancelled_ot(self):
        # Make sur that a cancel method won't be published
        self.ot_burgonde_1.cancel()
        self.schedule_burgonde.set_to_accepted()
        self.schedule_burgonde.publish_work_entries()

        burgonde_we = self.env["hr.work.entry"].search(
            [("employee_id", "=", self.roi_burgonde.id)]
        )
        self.assertEqual(len(burgonde_we), 1)
