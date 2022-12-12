### Description
This module adds a method to the model 'hr.payslip' that computes the withholding tax due each month. 

### Salary Rule
This method is supposed to be called in a salary rule, in order to return the withholding tax due on each payslip. Here is the code snipet to input in Odoo :
- `result = -compute_withholding_taxes_thailand(employee, payslip, categories)`

### Detail about computation
##### Previous Months Salary
- All previous payslips GROSS add together 
- If the employee joined this year, and worked before, also adds the previous revenue
##### Estimating Future Salary

- For monthly wages : multiply the wage in the contract by the number of months left
- For other types of wages : multiply the BASIC of the current payslip by the number of months left
##### Computing Allowance

This module is computing the allowance to deduct to the revenue in order to calculate the taxable income. It is using the fields added by the module hr_employee_withholding_tax_th in order to compute the allowance as per the thai law (2022).

##### Computing Tax
Once the taxable income known, the module can compute the yearly tax due by the employee. Once again, this is based on the thai law (2022). 