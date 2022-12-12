from odoo import models, fields


class EmployeeNickname(models.Model):
    _inherit = "hr.employee"

    titles = [
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
        ("Miss", "Miss"),
    ]

    title = fields.Selection(titles, string="Title", groups="hr.group_hr_user")
