"""
Extands the payslip model to calculate the withholded taxes according to the thai law.
Line to enter in the Salary Rule : `result = -compute_withholding_taxes_thailand(employee, payslip, categories)`
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_round
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
import traceback


class PayslipThailand(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        """
        Make the function available in odoo
        """
        res = super()._get_base_local_dict()
        res.update({
            'compute_withholding_taxes_thailand': compute_withholding_taxes_thailand
        })
        return res

def compute_withholding_taxes_thailand(employee, payslip, categories):
    """
    Compute the expected yearly salary
    Calculate the total allowance
    Calculate the total taxes to pay
    """
    employee_payslips = payslip.env['hr.payslip'].search([
        ('employee_id', '=', employee.id),
        '|',
        ('state', '=', 'done'),
        ('state', '=', 'paid'),
    ])
    taxes = (
        monthly_taxes_to_pay(payslip, categories, employee_payslips, employee)
        if not payslip.contract_id.use_forecast
        else payslip.contract_id.yearly_taxes / 12
    )
    return taxes

def monthly_taxes_to_pay(payslip, categories, employee_payslips, employee):
    """
    Deduct from the yearly taxes, and the taxes already payed, the taxes due this month.
    """
    yearly_taxes = yearly_taxes_to_pay(payslip, categories, employee_payslips, employee)
    taxes_paid = read_lines(employee_payslips, 'WITHHOLDING_TAX', payslip.date_to) + (
        employee.previous_withholding_tax if employee.first_year and employee.worked_before else 0)
    taxes_left = yearly_taxes + taxes_paid

    month_end = 12
    if payslip.contract_id.date_end and payslip.contract_id.date_end.year == payslip.date_from.year:
        month_end = payslip.contract_id.date_end.month

    taxes_to_pay_this_month = taxes_left / (month_end-(payslip.date_to.month-1))
    return max(taxes_to_pay_this_month, 0)

def read_lines(employee_payslips, line_code, date_to):
    tot = 0
    for payslip in employee_payslips:
        for line in payslip.line_ids:
            if line.code == line_code and line.date_to.month <= date_to.month and line.date_to.year == date_to.year:
                tot += line.amount
    return tot

def pay_frequency(freq):
        freq_dict = {'monthly': 1, 'quarterly': 1/3, 'semi-annually': 1/6, 'annually': 0,
            'weekly': 4, 'bi-weekly': 2, 'bi-monthly': 1/2}
        return freq_dict[freq]

def monthly_basic(payslip):
    first_day_of_the_month = payslip.date_from.replace(day=1)
    first_day_of_next_month = (payslip.date_from + relativedelta(months=1)).replace(day=1)
    payslips = payslip.env['hr.payslip'].search([
        ('employee_id', '=', payslip.employee_id),
        ('date_from', '>=', first_day_of_the_month),
        ('date_to', '<', first_day_of_next_month),
        '|',
        ('state', '=', 'done'),
        ('state', '=', 'paid'),
    ])
    return read_lines(payslips, 'GROSS', first_day_of_next_month)

def forecast_yearly_gross_salary(payslip, categories, employee_payslips, employee):
    """
    Estimate, from the employee's contract, the past gross salary and the gross salary
    from this payslip, the yearly income of the employee.
    If the employee doesn't have a monthly wage, it will multiply the basic salary of
    the month of the current payslip, and multiply it by the number of months left in
    the year in order to estimate the forecast gross salary.
    """
    previous_months_gross = read_lines(
        employee_payslips, 'GROSS', payslip.date_to.replace(day=1) - timedelta(days=1)) + (
            employee.previous_revenue if employee.first_year and employee.worked_before else 0)
    this_slip_gross = categories.GROSS

    month_start = payslip.date_from.month
    month_end = (
        payslip.contract_id.date_end.month
        if payslip.contract_id.date_end and payslip.contract_id.date_end.year == payslip.date_from.year
        else 12
    )

    nb_months_left = month_end - month_start + 1
    schedule_pay = payslip.contract_id.structure_type_id.default_schedule_pay

    forecast_gross = (
        pay_frequency(schedule_pay) * (
            payslip.contract_id.wage if payslip.contract_id.wage_type == 'monthly'
            else this_slip_gross
        ) if pay_frequency(schedule_pay) <= 1
        else (this_slip_gross + monthly_basic(payslip))
    ) * nb_months_left

    yearly_gross = previous_months_gross + forecast_gross
    return yearly_gross

def yearly_taxes_to_pay(payslip, categories, employee_payslips, employee):
    """
    Deduct form the yearly estimate salary (not estimated if we are in december) the total
    taxes due this year.
    """
    forecast_gross = forecast_yearly_gross_salary(payslip, categories, employee_payslips, employee)
    allowance = compute_allowance(employee, forecast_gross, payslip.contract_id)
    yearly_taxes = compute_income_tax(max(0, forecast_gross - allowance))
    return yearly_taxes

def compute_allowance(employee, tot_gross_income, contract):
    """
    Compute the allowance, according to the values recorded in the employee sheet.
    It computes it from the yearly estimated salary.
    """
    tot_allowance = 0
    if employee.expenses:
        tot_allowance += min(tot_gross_income * 0.5, 100000)
    if employee.personal_allowance:
        tot_allowance += 60000
    if employee.spouse_allowance:
        tot_allowance += 60000
    
    if employee.parents_allowance > 0:
        tot_allowance += 30000*employee.parents_allowance
    if employee.children_before_2018 > 0:
        tot_allowance += 30000*employee.children_before_2018
    if employee.children_since_2018 >0:
        tot_allowance += 60000*employee.children_since_2018
    if employee.insurance_premium > 0:
        tot_allowance += min(employee.insurance_premium, 100000)
    if employee.provident_fund > 0:
        tot_allowance += min(employee.provident_fund, 10000)
    if employee.housing_loan > 0:
        tot_allowance += min(employee.housing_loan, 100000)
    if employee.provident_fund_retirement_mutual_fund > 0:
        tot_allowance += min(employee.provident_fund_retirement_mutual_fund, tot_gross_income*0.3, 500000)
    if employee.ssf > 0:
        tot_allowance += min(employee.ssf, tot_gross_income*0.3, 500000)
    
    if employee.donations > 0:
        tot_allowance += min((tot_gross_income-tot_allowance)*0.1, employee.donations)
    
    tot_allowance += (750 * (
        12 if contract.date_start.year < datetime.today().year else 13 - contract.date_start.month)) + (
            employee.previous_social_security if employee.first_year and employee.worked_before else 0)
    return tot_allowance

def convert_to_month(value):
    return float_round(value / 12.0, precision_rounding=0.01, rounding_method='DOWN')

def compute_income_tax(taxable_income):
    """
    Compute the tax to pay on the entire year.
    The input of this method should be the yearly taxable salary, after allowances.

    Has been checked on UOB income taxe calculator :
    https://www.uobam.co.th/en/tax-calculation
    """
    if taxable_income < 0:
        raise UserError('Taxable income can\'t be negative.')
    try:
        tot_tax = 0
        previous = 0
        TAX_DISTRIBUTION = (
            (0, 150000),
            (0.05, 300000),
            (0.1, 500000),
            (0.15, 750000),
            (0.2, 1000000),
            (0.25, 2000000),
            (0.3, 5000000),
            (0.35, None)
        )

        for rate, limit in TAX_DISTRIBUTION:
            if limit is None:
                break
            if taxable_income <= limit:
                break
            tot_tax += rate * (limit - previous)
            previous = limit
        tot_tax += rate * (taxable_income - previous)
        return tot_tax

    except ValueError as e:
        raise e('The taxable income must be a float or an integer')
