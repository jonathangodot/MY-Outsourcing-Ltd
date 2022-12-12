from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class HrOvertimeNeed(models.Model):
    _name = "hr.overtime.need"
    _inherit = ["mail.thread"]
    _description = """
Describe a need for overtime. It is mainly composed of a list of schedules, supposed
to fill a number of hours required.
"""

    states = [
        ("DRAFT", "Draft"),
        ("VALIDATED", "Validated"),
        ("OVER", "Over"),
    ]

    name = fields.Char(
        string="Name",
        required=True,
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
    )
    hours_needed = fields.Float(
        string="Tot. Hours",
        default=10,
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
        tracking=True,
    )
    hours_filled = fields.Float(
        string="Hours Filled",
        readonly=True,
        default=0,
        compute="_compute_hours_filled",
        store=True,
    )
    hours_completed = fields.Boolean(
        string="Hours Completed", compute="_compute_hours_completed"
    )
    percentage_filled = fields.Percent(
        string="Allocated",
        default=0,
        readonly=True,
        compute="_compute_percentage_filled",
        store=True,
        digits=("EasterEgg", 2),
    )
    date_from = fields.Date(
        string="Date From",
        tracking=True,
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
    )
    date_to = fields.Date(
        string="Date To",
        tracking=True,
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
    )
    state = fields.Selection(states, string="State", default="DRAFT", tracking=True)
    ot_schedules = fields.One2many(
        "hr.overtime.schedule",
        "ot_need",
        string="Overtime Schedule",
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
    )
    description = fields.Text(
        string="Description", readonly=True, states={"DRAFT": [("readonly", False)]}
    )

    def set_to_draft(self):
        for record in self:
            record.state = "DRAFT"
            record.count_hours()

    def set_to_validated(self):
        for record in self:
            record.state = "VALIDATED"

    def set_to_over(self):
        for record in self:
            record.state = "OVER"

    @api.depends("hours_filled", "hours_needed")
    def _compute_hours_completed(self):
        for record in self:
            record.hours_completed = record.hours_filled >= record.hours_needed

    @api.depends(
        "hours_needed",
        "ot_schedules",
        "state",
        "ot_schedules.state",
        "ot_schedules.ot",
    )
    def _compute_hours_filled(self):
        for record in self:
            record.count_hours()

    @api.onchange("ot_schedules")
    def _updating_schedules(self):
        for record in self:
            record.set_to_draft()

    def count_hours(self):
        """Count the hours filled for the overtime need"""
        self.ensure_one()
        hours_filled = 0
        for schedule in self.ot_schedules:
            hours_filled += schedule.nb_hours if schedule.state != "DRAFT" else 0
        self.hours_filled = hours_filled

    @api.depends("hours_needed", "hours_filled")
    def _compute_percentage_filled(self):
        for record in self:
            if record.hours_needed == 0:
                raise ValidationError(_("The hours needed cannot be 0."))
            record.percentage_filled = (
                record.hours_filled / record.hours_needed * 100.00
            )

    @api.onchange("date_from", "date_to", "ot_schedules")
    def _set_to_over(self):
        for record in self:
            record.check_over()
            record.check_no_ot_after()
            record.check_no_ot_before()

    def check_no_ot_after(self):
        """Makes sure the date to is after all the OT programmed in the schedules."""
        for record in self:
            if record.date_to:
                for schedule in record.ot_schedules:
                    if schedule.date_stop > datetime.combine(
                        record.date_to, datetime.max.time()
                    ):
                        raise UserError(
                            _(
                                "There is at least one overtime schedule that ends after the date to."
                            )
                        )

    def check_no_ot_before(self):
        """Makes sure the date from is before all the OT programmed in the schedules."""
        for record in self:
            if record.date_from:
                for schedule in record.ot_schedules:
                    if schedule.date_start < datetime.combine(
                        record.date_from, datetime.min.time()
                    ):
                        raise UserError(
                            _(
                                "There is at least one overtime schedule that starts before the date from."
                            )
                        )

    def check_over(self):
        """Check if the date to is passed and set the state to over if it is."""
        self.ensure_one()
        if self.date_to:
            if self.date_to < fields.Date.today():
                self.set_to_over()

    def cron_set_ot_over(self):
        """Cron executed every day to check if any overtime need is over."""
        records = self.env["hr.overtime.need"].search([])
        for record in records:
            record.check_over()

    def publish_all_work_entries(self):
        """Publish all the work entries of the schedules of the overtime need."""
        self.ensure_one()
        for schedule in self.ot_schedules:
            schedule.publish_work_entries()
