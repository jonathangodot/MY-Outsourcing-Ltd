from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class ThailandSPS110Company(models.Model):
    _name = "thailand.sps1.10.company"
    _inherit = "thailand.compliance.payroll.common"
    _description = "SPS1.10 Company"
    _order = "year desc"

    sps1_10_id = fields.One2many(
        "thailand.sps1.10", "company_report", string="Branch Report"
    )

    def _serialize(self):
        serialized = self.serialize()
        for sps1_10 in self.sps1_10_id:
            serialized.update(sps1_10._serialize())
        serialized = self.clean_serialized(serialized)
        serialized = self.format_serialized_float(serialized)
        return serialized

    def pdf_export_sps1_10(self):
        self.ensure_one()
        pass
        # data = self._serialize()
        # return self.env.ref('thai_compliance_payroll.thailand_pnd1_month_employees_pdf').report_action(self)

    @api.onchange("sps1_10_id")
    def _compute_no(self):
        for rec in self:
            i = 1
            for line in rec.sps1_10_id:
                line.no = i
                i += 1
