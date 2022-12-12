from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def create(self, vals):
        if vals.get("res_model") == "hr.overtime.schedule":
            schedule = self.env["hr.overtime.schedule"].browse(vals["res_id"])
            vals[
                "name"
            ] = f"{schedule.name} - {str(schedule.date_start)} - {str(schedule.date_stop)}"
            schedule.document_uploaded = True
        return super(IrAttachment, self).create(vals)

    def unlink(self):
        for record in self:
            if record.res_model == "hr.overtime.schedule":
                other_attachments = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "hr.overtime.schedule"),
                        ("res_id", "=", record.res_id),
                    ]
                )
                if len(other_attachments) == 1:
                    schedule = self.env["hr.overtime.schedule"].browse(record.res_id)
                    schedule.document_uploaded = False
                    schedule.state = "ACCEPTED"
        return super(IrAttachment, self).unlink()
