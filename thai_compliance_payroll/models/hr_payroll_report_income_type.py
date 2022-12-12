from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ..utils.const import WTC_LINES, PND1_LINES, MODELS_WITH_CUSTOM_FIELDS
import logging

_logger = logging.getLogger(__name__)


class HrPayrollReportIncomeType(models.Model):
    _name = "hr.payroll.report.income.type"
    _description = "Payroll Report Income Type"

    name = fields.Char(string="Name", required=True)
    model_field_name = fields.Char(
        string="Field Name", compute="_compute_model_field_name", store=True
    )
    salary_rule = fields.One2many(
        "hr.salary.rule", "thai_compliance_income_type", string="Salary Rule"
    )

    @api.depends("name")
    def _compute_model_field_name(self):
        """Set model field name in database"""
        for record in self:
            self.model_field_name = self.compute_model_field_name(record.name)

    def compute_model_field_name(self, field_name):
        """Compute model field name"""
        return f'x_{field_name.replace(" ", "_").lower()}'

    def add_field_in_model(self, field_name, model_name):
        """Create a field named field_name in model model_name"""
        field = self.env["ir.model.fields"].create(
            {
                "name": field_name,
                "model": model_name,
                "model_id": self.env["ir.model"]
                .search([("model", "=", model_name)])
                .id,
                "field_description": field_name.replace("x_", "")
                .replace("_", " ")
                .title(),
                "ttype": "monetary",
            }
        )
        if model_name == "thailand.pnd1.month":
            field.write(
                {
                    "depends": "attachment_line",
                    "compute": "{}{}{}".format(
                        "for record in self:\n",
                        f"\trecord['{field_name}'] = sum(\n",
                        f"\t\trecord.attachment_line.mapped('{field_name}'.replace('total_', '')))",
                    ),
                }
            )

    def add_field_in_view(self, field_name, view_name, place_holder):
        """Write field named field_name in view named view_name.
        Placeholders have been placed in the view in the form of
        comments to make it easier to add fields."""
        view = self.env["ir.ui.view"].search([("name", "=", view_name)])
        view.write(
            {
                "arch_base": view.arch_base.replace(
                    "<!-- {} -->".format(place_holder),
                    '<!-- {} --><field name="{}" sum="Tot. {}"/>'.format(
                        place_holder,
                        field_name,
                        field_name.replace("x_", ""),
                    ),
                )
            }
        )

    def remove_field_from_model(self, field_name, model_name):
        """Remove field named field_name in model model_name"""
        self.env["ir.model.fields"].search(
            [
                ("name", "=", field_name),
                ("model", "=", model_name),
            ]
        ).unlink()

    def remove_field_from_view(self, field_name, view_name):
        """Remove field named field_name in view named view_name"""
        self.ensure_one()
        view = self.env["ir.ui.view"].search([("name", "=", view_name)])
        view.write(
            {
                "arch_base": view.arch_base.replace(
                    '<field name="{}" sum="Tot. {}"/>'.format(
                        field_name,
                        field_name.replace("x_", ""),
                    ),
                    "",
                )
            }
        )

    def add_field(self, model, field_name):
        """Add field in model and view"""
        self.add_field_in_model(field_name, model["name"])
        for view_name in model["views"]:
            self.add_field_in_view(field_name, view_name, model["place_holder"])

    def remove_field(self, record, model):
        """Remove field from model and view"""
        field_name = self.compute_model_field_name(f"{model['prefix']}{record.name}")
        for view_name in model["views"]:
            record.remove_field_from_view(
                field_name,
                view_name,
            )
        record.remove_field_from_model(field_name, model["name"])
        return field_name

    #####
    ## Overriding

    @api.model
    def create(self, vals):
        """Override create() method to create custom field on model and view"""
        for model in MODELS_WITH_CUSTOM_FIELDS:
            field_name = self.compute_model_field_name(
                f"{model['prefix']}{vals['name']}"
            )
            self.add_field(model, field_name)
        return super(HrPayrollReportIncomeType, self).create(vals)

    def unlink(self):
        """Override unlink() method to delete custom field from model and view"""
        for record in self:
            for model in MODELS_WITH_CUSTOM_FIELDS:
                self.remove_field(record, model)
        return super(HrPayrollReportIncomeType, self).unlink()

    def write(self, vals):
        """Override write() method to update custom field in model and view"""
        for rec in self:
            for model in MODELS_WITH_CUSTOM_FIELDS:
                if "name" in vals:
                    field_name = self.remove_field(rec, model)
                    rec.add_field(model, field_name)
        return super().write(vals)
