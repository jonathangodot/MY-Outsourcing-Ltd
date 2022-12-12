from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class EmployeeNickname(models.Model):
    _inherit = "hr.employee"

    nickname = fields.Char("Nickname", groups="hr.group_hr_user")
