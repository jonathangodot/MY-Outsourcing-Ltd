from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class EmployeeGivenName(models.Model):
    _inherit = "hr.employee"

    ss_subscription_date = fields.Date("Subscription Date", groups="hr.group_hr_user")
    ss_no = fields.Char("Social Security Number", groups="hr.group_hr_user")

    @api.constrains("ss_no")
    def _check_ss_no(self):
        for record in self:
            if record.ss_no:
                if len(record.ss_no) != 13:
                    raise ValidationError(_("Social Security Number must be 13 digits"))
                if not record.ss_no.isdigit():
                    raise ValidationError(
                        _("Social Security Number must be digits only")
                    )

    def format_ss_no(self) -> str:
        """Format the SS number"""
        self.ensure_one()
        return (
            "{} {} {} {} {}".format(
                self.ss_no[0],
                self.ss_no[1:5],
                self.ss_no[5:10],
                self.ss_no[10:12],
                self.ss_no[12],
            )
            if self.ss_no
            else ""
        )
