from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    # Override existing
    street = fields.Char(string="Lane / Soi")
    street2 = fields.Char(string="Road")
    zip = fields.Char(change_default=True)
    city = fields.Char(string="Sub-District")
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one("res.country", string="Country", ondelete="restrict")
    country_code = fields.Char(related="country_id.code", string="Country Code")

    # New fields
    building = fields.Char(string="Building Name / Village")
    room_no = fields.Char(string="Room No.")
    floor = fields.Char(string="Floor")
    address_no = fields.Char(string="No.")
    address_moo = fields.Char(string="Moo.")
    district = fields.Char(string="District")
    province = fields.Char(string="Province")
    village = fields.Char(string="Village")
    fax = fields.Char(string="Fax")

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return [
            "building",
            "room_no",
            "floor",
            "address_no",
            "address_moo",
            "district",
            "province",
            "street",
            "street2",
            "city",
            "zip",
            "state_id",
            "country_id",
            "village",
        ]
