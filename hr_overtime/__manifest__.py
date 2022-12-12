# TODO : make this module independant from payroll
{
    "name": "Overtime",
    "version": "15.0.3.0.0",
    "summary": "Manage Employee Overtime",
    "category": "Human resources",
    "author": "Louis de Gislain de Bontin",
    "company": "Newlogic",
    "website": "https://www.newlogic.com",
    "depends": [
        "hr_payroll",
        "vendor_ks_percent_field",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/need_over.xml",
        "data/schedule_over.xml",
        "views/menu.xml",
        "views/hr_overtime_needs_views.xml",
        "views/hr_overtime_schedule_views.xml",
        "views/hr_overtime_views.xml",
    ],
    "license": "Other proprietary",
    "installable": True,
    "auto_install": False,
    "application": True,
}
