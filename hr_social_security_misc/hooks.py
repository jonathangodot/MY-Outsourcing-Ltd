from odoo import _, api, SUPERUSER_ID


def test_post_init_hook(cr, registry):
    """Create forlders and move templates in."""
    env = api.Environment(cr, SUPERUSER_ID, context={})
    param_obj = env["ir.config_parameter"]
    param_obj.set_param("ss_rate", 5)
