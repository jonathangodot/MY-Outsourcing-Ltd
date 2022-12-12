from faulthandler import cancel_dump_traceback_later
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError, UserError

from ..utils import utils_date
import pytz
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = """
This is the model for the Overtime. It is used to store the data for the Overtime.
"""

    states = [
        ("DRAFT", "Draft"),
        ("ACCEPTED", "Accepted"),
        ("VALIDATED", "Validated"),
        ("OVER", "Over"),
    ]
    cancelled_choices = [
        ("Y", "Cancelled"),
        ("N", ""),
    ]

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", compute="_compute_employee_id", store=True
    )
    ot_schedule = fields.Many2one(
        "hr.overtime.schedule",
        string="Schedule",
        readonly=True,
        required=True,
        ondelete="cascade",
    )
    hours = fields.Float(
        string="Hours", readonly=True, compute="_compute_hours", store=True
    )

    date_start = fields.Datetime(
        string="Date Start",
        required=True,
        default=(datetime.now() + timedelta(days=1)).replace(
            minute=0, second=0, microsecond=0
        ),
    )
    date_stop = fields.Datetime(
        string="Date Stop",
        required=True,
        default=(datetime.now() + timedelta(days=1, hours=2)).replace(
            minute=0, second=0, microsecond=0
        ),
    )

    tz = fields.Selection(
        "_tz_get",
        string="Timezone",
        required=True,
        default=lambda self: self.env.user.tz or "UTC",
    )
    work_entry_type_id = fields.Many2one(
        "hr.work.entry.type", string="Work Entry Type", required=True
    )

    state = fields.Selection(states, string="State", compute="_compute_state")
    cancelled = fields.Selection(
        cancelled_choices, string="Cancelled", default="N", readonly=True
    )

    @api.model
    def _tz_get(self):
        """Returns all the timezones"""
        return [(x, x) for x in pytz.all_timezones]

    def repeat(self, days):
        """Duplicate the current OT with an offset of <days> days."""
        self.ensure_one()
        self.create(
            {
                "ot_schedule": self.ot_schedule.id,
                "date_start": self.date_start + timedelta(days=days),
                "date_stop": self.date_stop + timedelta(days=days),
                "tz": self.tz,
                "work_entry_type_id": self.work_entry_type_id.id,
            }
        )
        self.ot_schedule.set_to_draft()

    def repeat_next_day(self):
        """Duplicate the current OT and set the date_start and date_stop to the next day."""
        self.repeat(days=1)

    def repeat_next_week(self):
        """Duplicate the current OT and set the date_start and date_stop to the next week."""
        self.repeat(days=7)

    @api.constrains("date_start", "date_stop")
    def _check_dates(self):
        """Calls several methods to make sur the dates won't create any conflict."""
        for record in self:
            record.check_dates()
            record.check_need_date()

    def check_need_date(self):
        """If the OT's schedule has a Need, makes sure the OT is in the date range of the Need."""
        for record in self:
            if record.ot_schedule.ot_need and record.ot_schedule.ot_need.date_to:
                date_to = datetime.combine(
                    record.ot_schedule.ot_need.date_to, datetime.max.time()
                )
                if record.date_stop > date_to:
                    raise ValidationError(
                        _(
                            "OT end : (%(stop)s) must be before the date to : (%(limit)s).",
                            stop=record.date_stop,
                            limit=date_to,
                        )
                    )

    def check_dates(self):
        """Makes sure the OT's dates don't overlap, and that the date stop is later than the date start."""

        def date_range_overlap(a_start, a_end, b_start, b_end):
            if (
                a_start <= b_start
                and b_start <= a_end
                #
                or a_start <= b_end
                and b_end <= a_end
                #
                or b_start <= a_start
                and a_end <= b_end
            ):
                return True
            else:
                return False

        for record in self:
            if record.date_stop and record.date_start >= record.date_stop:
                raise ValidationError(
                    _(
                        "Start date (%(start)s) must be earlier than overtime end date (%(end)s).",
                        start=record.date_start,
                        end=record.date_stop,
                    )
                )

        employee_ots = self.env["hr.overtime"].search(
            [
                ("employee_id", "=", self.ot_schedule.employee_id.id),
            ]
        )
        dates = [(ot.date_start, ot.date_stop) for ot in employee_ots]
        for i in range(0, len(dates)):
            for j in range(i + 1, len(dates)):
                if dates[i][0] and dates[i][1] and dates[j][0] and dates[j][1]:
                    if date_range_overlap(
                        dates[i][0], dates[i][1], dates[j][0], dates[j][1]
                    ):
                        raise ValidationError(
                            _(
                                'One OT for employee {} (Schedule "{}") is overlapping :\n{} || {}\n{} || {}.'.format(
                                    self.ot_schedule.employee_id.name,
                                    self.ot_schedule.name,
                                    utils_date.utc_to_timestamp(dates[i][0], record.tz),
                                    utils_date.utc_to_timestamp(dates[i][1], record.tz),
                                    utils_date.utc_to_timestamp(dates[j][0], record.tz),
                                    utils_date.utc_to_timestamp(dates[j][1], record.tz),
                                )
                            )
                        )
                j += 1
            i += 1

    @api.depends("ot_schedule", "write_date")
    def _compute_employee_id(self):
        # TODO : duplicate with method `update_employee_ot` on the model schedule
        for record in self:
            record.compute_employee_id()

    def compute_employee_id(self):
        for record in self:
            record.employee_id = record.ot_schedule.employee_id

    @api.depends("date_start", "date_stop", "tz")
    def _compute_hours(self):
        """Count the time that this OT lasts."""
        for record in self:
            record.hours = (record.date_stop - record.date_start).total_seconds() / 3600

    @api.depends("ot_schedule")
    def _compute_state(self):
        """Compute the state of the OT."""
        for record in self:
            record.state = record.ot_schedule.state

    def count_hours(self):
        for record in self:
            record.ot_schedule.count_hours()
            if record.ot_schedule.ot_need:
                record.ot_schedule.ot_need.count_hours()

    def cancel(self):
        """Cancel the OT."""
        self.cancelled = "Y"
        self.count_hours()

    def revert_cancel(self):
        """Revert the cancelation of the OT."""
        self.cancelled = "N"
        self.count_hours()
