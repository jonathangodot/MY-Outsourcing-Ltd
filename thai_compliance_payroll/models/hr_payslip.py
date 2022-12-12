# -*- coding:utf-8 -*-

from odoo import fields, models, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    pnd1_month = fields.Many2one("thailand.pnd1.attachment.line", string="PND1")
