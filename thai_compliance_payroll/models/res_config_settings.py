from odoo import models, fields, api, _


class ThaiCompliancePayrollSettings(models.TransientModel):
    """
    Adds a few settings options for the user, in order to make the link between attendance and work entries.
    """

    _inherit = "res.config.settings"

    code_gross = fields.Char(
        string="Code Gross",
        default="GROSS",
        help="Must be similar to the one used in the salary rules.",
        config_parameter="thai_compliance_payroll.code_gross",
    )
    code_tax = fields.Char(
        string="Code Tax",
        default="PT",
        help="Must be similar to the one used in the salary rules.",
        config_parameter="thai_compliance_payroll.code_tax",
    )
    code_secu = fields.Char(
        string="Code Social Security",
        default="SS",
        help="Must be similar to the one used in the salary rules.",
        config_parameter="thai_compliance_payroll.code_secu",
    )
