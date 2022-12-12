from odoo import api, fields, models, _


class HrPayrollStructureType(models.Model):
    _inherit = "hr.payroll.structure.type"

    tax_3_percent = fields.Boolean(string="3% Withholding Tax", default=False)
    count_in_pnd1 = fields.Boolean(string="Count in PND1", default=True)
    count_in_sps1_10 = fields.Boolean(string="Count in SPS1-10", default=True)
