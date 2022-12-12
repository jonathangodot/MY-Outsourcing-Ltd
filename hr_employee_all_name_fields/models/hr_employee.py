from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _concat_names(self):
        self.ensure_one()
        return f"{self.given_names} {self.family_name}"
