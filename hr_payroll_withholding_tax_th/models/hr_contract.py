from site import execsitecustomize
from odoo import api, fields, models, _
from .hr_payslip import compute_allowance, compute_income_tax

import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'hr.contract'

    use_forecast = fields.Boolean(string='Estimate Forecast', default=False,
        help='If checked, the yearly taxes will be estimated based on the next field : Estimated Tot. Income.')
    estimated_total_income = fields.Monetary(string='Estimated Tot. Income', default=0,
        help='Estimated total MONTHLY income for the year. This is used to estimate the withholding tax.')
    yearly_taxes = fields.Monetary(string='Yearly Taxes', default=0, compute='_compute_yearly_taxes',
        help='This is the yearly taxes to pay. It is computed based on the estimated total income.' +\
            'When computing the payslip, Odoo divide this value by 12 in order to compute the monthly taxes to pay.')
    yearly_taxes_percentage = fields.Percent(string='Estimated yearly PIT', default=0,
        compute='_compute_yearly_taxes', digits=('BTC2zeMoon', 2),
        help='Compare the yearly taxes to pay with the estimated total income.')

    @api.depends('estimated_total_income')
    def _compute_yearly_taxes(self):
        for contract in self:
            if contract.use_forecast and contract.estimated_total_income > 0:
                yearly_income = contract.estimated_total_income*12
                allowance = compute_allowance(contract.employee_id, yearly_income, contract)

                contract.yearly_taxes = compute_income_tax(yearly_income-allowance)
                contract.yearly_taxes_percentage = contract.yearly_taxes / yearly_income * 100
            else:
                contract.yearly_taxes = 0
                contract.yearly_taxes_percentage = 0
