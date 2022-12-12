from odoo import models, fields, api, _
from odoo.addons.base.models.ir_module import assert_log_admin_access
from ..utils.const import MODELS_WITH_CUSTOM_FIELDS
import logging

_logger = logging.getLogger(__name__)


class Module(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    def button_immediate_upgrade(self):
        """Override button_immediate_upgrade() in order to conserve the custom fields on the views.
        We have to do so, otherwise the views would be reseted, and the custom fields would disapear."""
        res = super(Module, self).button_immediate_upgrade()
        fields = self.env["hr.payroll.report.income.type"].search([])
        for field in fields:
            for model in MODELS_WITH_CUSTOM_FIELDS:
                for view_name in model["views"]:
                    fields.add_field_in_view(
                        field.compute_model_field_name(
                            f"{model['prefix']}{field.name}"
                        ),
                        view_name,
                        model["place_holder"],
                    )
        return res
