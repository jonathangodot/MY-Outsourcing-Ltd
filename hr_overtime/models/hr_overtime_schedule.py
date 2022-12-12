from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError

from .hr_overtime_need import HrOvertimeNeed

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class HrOvertimeSchedule(models.Model):
    _name = "hr.overtime.schedule"
    _inherit = ["mail.thread"]
    _description = """
This is the schedule of overtime for an employee. An employee can have many schedules,
It is composed by as much overtime object as needed.
"""

    states = [
        ("DRAFT", "Draft"),
        ("ACCEPTED", "Accepted"),
        ("VALIDATED", "Validated"),
        ("OVER", "Over"),
    ]

    name = fields.Char(
        string="Name",
        readonly=True,
        compute="_compute_name",
        store=True,
        states={"DRAFT": [("readonly", False)]},
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        readonly=True,
        states={"DRAFT": [("readonly", False)]},
        tracking=True,
    )

    nb_hours = fields.Float(
        string="Hours of OT", compute="_compute_nb_hours", store=True, readonly=True
    )

    date_start = fields.Datetime(
        string="Date Start", readonly=True, compute="_compute_date_start", store=True
    )
    date_stop = fields.Datetime(
        string="Date Stop", readonly=True, compute="_compute_date_stop", store=True
    )

    ot = fields.One2many(
        "hr.overtime",
        "ot_schedule",
        string="Overtime",
        readonly=True,
        required=True,
        states={"DRAFT": [("readonly", False)]},
    )
    ot_need = fields.Many2one(
        "hr.overtime.need", string="Need", readonly=True, ondelete="set null"
    )
    ot_need_state = fields.Selection(
        HrOvertimeNeed.states, compute="_compute_ot_need_state", tracking=True
    )
    state = fields.Selection(
        states, string="Status", default="DRAFT", store=True, tracking=True
    )
    document_uploaded = fields.Boolean(string="Document Uploaded", readonly=True)

    def publish_work_entries(self):
        """Publish work entries for this schedule, returns an error if duplicate."""
        # TODO : mettre un bouton pour publier les work entries dans le menu action de la view list
        self.ensure_one()
        if self.state != "DRAFT":
            for ot in self.ot:
                slot = self.env["hr.work.entry"].search(
                    [
                        ("name", "=", f"{ot.work_entry_type_id.name} : {self.name}"),
                        ("employee_id", "=", ot.employee_id.id),
                        ("date_start", "=", ot.date_start),
                        ("date_stop", "=", ot.date_stop),
                        ("work_entry_type_id", "=", ot.work_entry_type_id.id),
                    ]
                )
                if len(slot) == 0 and ot.cancelled != "Y":
                    self.env["hr.work.entry"].create(
                        {
                            "name": f"{ot.work_entry_type_id.name} : {self.name}",
                            "employee_id": ot.employee_id.id,
                            "date_start": ot.date_start,
                            "date_stop": ot.date_stop,
                            "work_entry_type_id": ot.work_entry_type_id.id,
                        }
                    )

    def set_to_draft(self):
        for record in self:
            record.state = "DRAFT"

    def set_to_accepted(self):
        """Impossible to accept if there is no OT."""
        for record in self:
            if record.ot:
                record.state = "ACCEPTED"
            else:
                raise UserError(
                    _("You must create at least one overtime before accepting it.")
                )

    def set_to_over(self):
        for record in self:
            record.state = "OVER"

    def set_to_validated(self):
        for record in self:
            if record.document_uploaded:
                record.state = "VALIDATED"
            else:
                raise UserError(
                    _("You must upload a document before validating the schedule.")
                )

    @api.constrains("ot")
    def _check_if_ot_not_empty(self):
        for record in self:
            record.check_if_ot_not_empty()

    def check_if_ot_not_empty(self):
        for record in self:
            if not record.ot:
                raise ValidationError(
                    _(
                        "You must create at least one overtime before saving the schedule."
                    )
                )

    @api.depends("ot_need", "employee_id")
    def _compute_name(self):
        """The name is automatically composed with the name of the need and the employee name.
        The user can always choose to change it."""
        for record in self:
            employee = (
                record.employee_id.name if record.employee_id else "(Employee Name)"
            )
            prefix = (
                record.ot_need.name
                if record.ot_need
                else record.name.replace(f" - {employee}", "")
                if record.name and record.name[:2] != "OT"
                else "OT"
            )
            record.name = f"{prefix} - {employee}"
            if record.employee_id:
                record.name = record.name.replace(" - (Employee Name)", "")
            record.set_to_draft()

    @api.depends("ot")
    def _compute_nb_hours(self):
        for record in self:
            record.count_hours()

    def count_hours(self):
        """Count the total number of hours of overtime."""
        self.ensure_one()
        self.nb_hours = 0
        for ot in self.ot:
            self.nb_hours += ot.hours if ot.cancelled != "Y" else 0

    @api.depends("ot")
    def _compute_date_start(self):
        """Compute the date start of the schedule by fetching the earlies OT date start."""
        for record in self:
            if record.ot:
                record.date_start = min([ot.date_start for ot in record.ot])

    @api.depends("ot")
    def _compute_date_stop(self):
        """Compute the date stop of the schedule by fetching the latest OT date stop."""
        for record in self:
            if record.ot:
                record.date_stop = max([ot.date_stop for ot in record.ot])

    @api.depends("ot_need")
    def _compute_ot_need_state(self):
        for record in self:
            record.ot_need_state = record.ot_need.state if record.ot_need else "DRAFT"

    @api.onchange("ot")
    def _set_to_draft(self):
        """Status to draft if any OT is updated."""
        for record in self:
            record.set_to_draft()
            record.count_hours()

    @api.onchange("employee_id")
    def update_employee_ot(self):
        """Update the employee of all OTs to match the employee set to the schedule."""
        for record in self:
            for ot in record.ot:
                ot.employee_id = record.employee_id

    def check_over(self):
        """Check if the date to is passed and set the state to over if it is."""
        for record in self:
            if (
                record.date_stop
                and record.date_stop > datetime.now()
                and record.state != "DRAFT"
            ):
                break
        else:
            record.set_to_over()

    def cron_set_ot_over(self):
        """Cron executed every day to check if any overtime schedule is over."""
        records = self.env["hr.overtime.schedule"].search([])
        for record in records:
            record.check_over()

    def write(self, vals):
        if "employee_id" in vals:
            # TODO : duplicate with method `update_employee_ot`
            for ot in self.ot:
                ot.employee_id = vals["employee_id"]

        if "validation_document" in vals:
            self.state = "VALIDATED"
        return super(HrOvertimeSchedule, self).write(vals)
