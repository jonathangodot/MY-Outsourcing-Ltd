from .common import TestOTCommon
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


@tagged("ot", "newlogic")
class TestOTSchedule(TestOTCommon):
    @classmethod
    def setUpClass(self):
        super(TestOTSchedule, self).setUpClass()

    def test_schedule_methods(self):
        # Make sure that publishing work entries with draft state doesn't publish anything
        self.schedule_lott.publish_work_entries()
        lott_we = self.env["hr.work.entry"].search(
            [("employee_id", "=", self.roi_lott.id)]
        )
        self.assertEqual(len(lott_we), 0)

        # Make sure that publishing work entries with accepted state publishes work entries
        self.schedule_lott.set_to_accepted()
        self.assertEqual(self.schedule_lott.state, "ACCEPTED")
        self.schedule_lott.publish_work_entries()
        lott_we = self.env["hr.work.entry"].search(
            [("employee_id", "=", self.roi_lott.id)]
        )
        self.assertEqual(len(lott_we), 2)

        # Testing the methods that update the state of the schedule
        self.schedule_lott.set_to_draft()
        self.assertEqual(self.schedule_lott.state, "DRAFT")
        self.schedule_lott.set_to_accepted()
        self.assertEqual(self.schedule_lott.state, "ACCEPTED")
        self.schedule_lott.set_to_over()
        self.assertEqual(self.schedule_lott.state, "OVER")
        with self.assertRaises(UserError):
            self.schedule_lott.set_to_validated()

        # Validating or saving a schedule with no OT raise errors
        empty_schedule = self.ot_schedule_obj.create(
            {
                "employee_id": self.roi_lott.id,
            }
        )
        with self.assertRaises(ValidationError):
            empty_schedule.check_if_ot_not_empty()
        with self.assertRaises(UserError):
            empty_schedule.set_to_validated()

        # Associating a schedule to a need, and testing the method that generate the name of the schedule
        self.schedule_lott.ot_need = self.need
        self.assertEqual(self.schedule_lott.name, "Quete du Graal - Roi Lott")

        # Testing the count hours method
        self.schedule_lott.count_hours()
        self.assertEqual(self.schedule_lott.nb_hours, 4)
        self.schedule_lott.ot[0].cancelled = "Y"
        # Testing the count hours method with a cancelled OT (should not be counted)
        self.schedule_lott.count_hours()
        self.assertEqual(self.schedule_lott.nb_hours, 2)
        self.schedule_lott.ot[0].cancelled = "N"

        # Making sure that the computed fields were correctly computed
        self.assertEqual(self.schedule_lott.date_start, datetime(2022, 8, 1, 18, 0, 0))
        self.assertEqual(self.schedule_lott.date_stop, datetime(2022, 8, 2, 20, 0, 0))
        self.assertEqual(self.schedule_lott.state, "DRAFT")

        # Make sure that updating the employee on the schedule affects the OTs and the name
        self.schedule_lott.employee_id = self.roi_burgonde.id
        self.assertEqual(self.schedule_lott.name, "Quete du Graal - Roi Burgonde")
        for ot in self.schedule_lott.ot:
            self.assertEqual(ot.employee_id, self.roi_burgonde)
