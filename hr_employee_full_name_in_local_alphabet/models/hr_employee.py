from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    local_name = fields.Char("Full Name In Local Alphabet", groups="hr.group_hr_user")
