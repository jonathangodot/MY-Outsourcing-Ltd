from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class EmployeeNickname(models.Model):
    _inherit = "hr.employee"

    family_name = fields.Char("Family Name", groups="hr.group_hr_user")
