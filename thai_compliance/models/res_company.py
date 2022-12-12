from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    branch_nb = fields.Integer(string="Branch Number")
    pid = fields.Char(string="PID", help="Personal Identification No.")
    tin = fields.Char(string="TIN", help="Tax Identification No.")

    city = fields.Char(
        compute="_compute_address", inverse="_inverse_city", string="Sub-District"
    )
    # # New fields
    building = fields.Char(compute="_compute_address", inverse="_inverse_building")
    room_no = fields.Char(compute="_compute_address", inverse="_inverse_room_no")
    floor = fields.Char(compute="_compute_address", inverse="_inverse_floor")
    address_no = fields.Char(compute="_compute_address", inverse="_inverse_address_no")
    address_moo = fields.Char(
        compute="_compute_address", inverse="_inverse_address_moo"
    )
    district = fields.Char(compute="_compute_address", inverse="_inverse_district")
    province = fields.Char(compute="_compute_address", inverse="_inverse_province")
    village = fields.Char(compute="_compute_address", inverse="_inverse_village")
    fax = fields.Char(related="partner_id.fax", store=True, readonly=False)

    @api.constrains("pid", "tin")
    def _check_pid_tin(self):
        """Check PID and TIN format"""
        for rec in self:
            if rec.pid and len(rec.pid) != 13:
                raise ValidationError(_("PID must be 13 digits"))
            if rec.tin and len(rec.tin) != 10:
                raise ValidationError(_("TIN must be 10 digits"))

    def _get_company_address_field_names(self):
        """Return a list of fields coming from the address partner to match
        on company address fields. Fields are labeled same on both models."""
        return [
            "street",
            "street2",
            "city",
            "zip",
            "state_id",
            "country_id",
            "building",
            "room_no",
            "floor",
            "address_no",
            "address_moo",
            "district",
            "province",
            "village",
        ]

    def _inverse_building(self):
        for company in self:
            company.partner_id.building = company.building

    def _inverse_room_no(self):
        for company in self:
            company.partner_id.room_no = company.room_no

    def _inverse_floor(self):
        for company in self:
            company.partner_id.floor = company.floor

    def _inverse_address_no(self):
        for company in self:
            company.partner_id.address_no = company.address_no

    def _inverse_address_moo(self):
        for company in self:
            company.partner_id.address_moo = company.address_moo

    def _inverse_district(self):
        for company in self:
            company.partner_id.district = company.district

    def _inverse_province(self):
        for company in self:
            company.partner_id.province = company.province

    def _inverse_village(self):
        for company in self:
            company.partner_id.village = company.village
