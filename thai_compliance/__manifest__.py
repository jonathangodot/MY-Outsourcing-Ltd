{
    "name": "Thai Compliance",
    "version": "15.0.3.0.0",
    "summary": "Squeleton",
    "category": "Human resources",
    "author": "Louis de Gislain de Bontin",
    "company": "Newlogic",
    "website": "https://www.newlogic.com",
    "depends": [
        "hr_employee_all_name_fields",
        "mail",
        "l10n_th_amount_to_text",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/hr_employee_views.xml",
    ],
    "license": "Other proprietary",
    "installable": True,
    "auto_install": False,
    "application": True,
    "post_init_hook": "test_post_init_hook",
    "uninstall_hook": "test_uninstall_hook",
}