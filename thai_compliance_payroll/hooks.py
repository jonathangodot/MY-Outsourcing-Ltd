from odoo import _, api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def test_post_init_hook(cr, registry):
    """Make sure that the settings are set correctly and useable right after install."""
    env = api.Environment(cr, SUPERUSER_ID, context={})
    param_obj = env["ir.config_parameter"]
    param_obj.set_param("code_gross", "GROSS")
    param_obj.set_param("code_tax", "PT")
    param_obj.set_param("code_secu", "SS")
