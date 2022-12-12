from odoo import models, fields, api, _


class ThaiComplianceSSRate(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Thai Compliance Social Security Rate"

    ss_rate = fields.Float(
        string="Social Security Rate (%)",
        default=5,
        config_parameter="ss_rate",
    )
