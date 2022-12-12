# -*- coding:utf-8 -*-

from odoo import fields, models, _


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    thai_compliance_income_type = fields.Many2one(
        "hr.payroll.report.income.type", string="Income Type"
    )
