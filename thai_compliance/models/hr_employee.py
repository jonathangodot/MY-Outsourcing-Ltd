from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    tin = fields.Char(
        string="Tax Identification No", size=10, groups="hr.group_hr_user"
    )

    @api.constrains("identification_id")
    def _check_identification_id(self):
        """Check the PID format"""
        for rec in self:
            if rec.identification_id and len(rec.identification_id) != 13:
                raise ValidationError(_("The PID must be 13 characters long."))

    def format_pid(self) -> str:
        """Format the PID to fit the form"""
        self.ensure_one()
        return (
            "{} {} {} {} {}".format(
                self.identification_id[0],
                self.identification_id[1:5],
                self.identification_id[5:10],
                self.identification_id[10:12],
                self.identification_id[12],
            )
            if self.identification_id
            else ""
        )

    def format_tin(self) -> str:
        """Format the TIN to fit the form"""
        self.ensure_one()
        return (
            "{} {} {} {}".format(
                self.tin[0],
                self.tin[1:5],
                self.tin[5:9],
                self.tin[9],
            )
            if self.tin
            else ""
        )

    def format_address(self):
        """Format the address to fit the form"""
        self.ensure_one()
        partner = self.address_home_id
        return (
            (
                "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, Rm. : {}".format(
                    partner.building,
                    partner.village,
                    partner.address_no,
                    partner.address_moo,
                    partner.street,
                    partner.street2,
                    partner.city,
                    partner.district,
                    partner.province,
                    partner.zip,
                    partner.room_no,
                )
                .replace("False, ", "")
                .replace(", Rm. : False", "")
            )
            if partner
            else ""
        )
