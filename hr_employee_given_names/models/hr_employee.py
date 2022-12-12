from odoo import models, fields


class EmployeeGivenName(models.Model):
    _inherit = "hr.employee"

    given_names = fields.Char("Given Names", groups="hr.group_hr_user")
