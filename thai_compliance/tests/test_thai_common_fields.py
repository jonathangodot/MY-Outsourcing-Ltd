from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from .common import TestThaiComplianceCommon
from ..models import thailand_common_fields
from datetime import date, timedelta
from ..utils.const import *
import os
import base64, io
import logging
from ..utils.PyPDF2 import PdfReader

_logger = logging.getLogger(__name__)


@tagged("thai_compliance_common_fields", "newlogic", "thai_compliance")
class TestThaiComplianceCommonField(TestThaiComplianceCommon):
    @classmethod
    def setUpClass(self):
        super(TestThaiComplianceCommonField, self).setUpClass()

    def test_format_pid(self):
        self.assertEqual(
            self.common_obj.format_pid("1234567890123"),
            "1 2345 67890 12 3",
            "PID should be formatted correctly",
        )

    def test_format_wrong_pid(self):
        self.assertEqual(
            self.common_obj.format_pid(False),
            "",
            "PID should be empty",
        )

    def test_format_tin(self):
        self.assertEqual(
            self.common_obj.format_tin(False),
            "",
            "TIN should be empty",
        )

    def test_format_wrong_tin(self):
        self.assertEqual(
            self.common_obj.format_tin("1234567890"),
            "1 2345 6789 0",
            "TIN should be formatted correctly",
        )

    def test_format_address(self):
        self.assertEqual(
            self.common_doc_kaamelott.format_address(),
            "Chateau de Kaamelott, 666, 6, Graal Rd., Soi Excalibur, Logre, Kaamelott, In The Forest, 66666, Rm. : 1",
            "Address should be formatted correctly",
        )
        self.assertEqual(
            self.common_doc_aquitaine.format_address(),
            "Chateau d'Aquitaine, 777, 7, Aquitaine, On the coast, 77777",
            "Address should be formatted correctly",
        )

    def test_serialize_model(self):
        self.maxDiff = None
        self.assertEqual(
            self.common_doc_kaamelott.serialize(),
            {
                "year": "2021",
                "company_name": "Royaume de Logre",
                "company_address": "Chateau de Kaamelott, 666, 6, Graal Rd., Soi Excalibur, Logre, Kaamelott, In The Forest, 66666, Rm. : 1",
                "address_building": "Chateau de Kaamelott",
                "address_village": False,
                "address_room_no": "1",
                "address_floor_no": "1",
                "address_no": "666",
                "address_moo": "6",
                "address_street": "Graal Rd.",
                "address_road": "Soi Excalibur",
                "address_sub_district": "Logre",
                "address_district": "Kaamelott",
                "address_province": "In The Forest",
                "address_post_code": "66666",
                "company_pid": "1 2345 67890 12 3",
                "company_tin": "1 2345 6789 0",
                "branch_no": 0,
                "phone_no": False,
                "filled_day": date.today().day,
                "filled_month": date.today().month,
                "filled_year": date.today().year + 543,
                "position": False,
            },
            "Model should be serialized correctly",
        )

    def test_clean_serializer(self):
        self.maxDiff = None
        _logger.info(self.common_doc_kaamelott.serialize())
        self.assertEqual(
            self.common_doc_kaamelott.clean_serialized(
                self.common_doc_kaamelott.serialize()
            ),
            {
                "year": "2021",
                "company_name": "Royaume de Logre",
                "company_address": "Chateau de Kaamelott, 666, 6, Graal Rd., Soi Excalibur, Logre, Kaamelott, In The Forest, 66666, Rm. : 1",
                "address_building": "Chateau de Kaamelott",
                "address_room_no": "1",
                "address_floor_no": "1",
                "address_no": "666",
                "address_moo": "6",
                "address_street": "Graal Rd.",
                "address_road": "Soi Excalibur",
                "address_sub_district": "Logre",
                "address_district": "Kaamelott",
                "address_province": "In The Forest",
                "address_post_code": "66666",
                "company_pid": "1 2345 67890 12 3",
                "company_tin": "1 2345 6789 0",
                "filled_day": str(date.today().day),
                "filled_month": str(date.today().month),
                "filled_year": str(date.today().year + 543),
            },
            "Serializer should be cleaned correctly",
        )

    def test_associated_payslips(self):
        payslips = self.env["hr.payslip"].search(
            [
                ("company_id", "=", self.company_kaamelott.id),
                ("date_from", ">=", date(int(self.common_doc_kaamelott.year), 7, 1)),
                (
                    "date_to",
                    "<=",
                    date(int(self.common_doc_kaamelott.year), 7 + 1, 1)
                    + timedelta(days=-1),
                ),
                ("state", "in", ["done", "paid"]),
            ]
        )
        associated_slips = self.common_doc_kaamelott.associated_payslips(7, 7)
        self.assertEqual(len(payslips), len(associated_slips))
        for slip in associated_slips:
            self.assertIn(slip, payslips)

    def test_no_duplicates(self):
        with self.assertRaises(ValidationError):
            self.common_obj.create(
                {
                    "year": 2021,
                    "company_id": self.company_kaamelott.id,
                }
            )

    def test_fetch_contracts(self):
        self.assertEqual(
            self.common_doc_kaamelott.fetch_contracts(
                self.arthur, self.common_doc_kaamelott
            ),
            self.contract_arthur,
            "Contract should be fetched correctly",
        )

    def test_fetch_contract_not_running(self):
        self.assertEqual(
            self.common_doc_aquitaine.fetch_contracts(
                self.perceval, self.common_doc_kaamelott
            ),
            self.env["hr.contract"],
            "No contract should be returned",
        )

    def test_write_pdf(self):
        pdf_template = os.path.join(PATH_TEMPLATE, "pnd1_en.png")
        self.common_doc_kaamelott.write_pdf(pdf_template, "out_test.pdf")
        attachment = self.env["ir.attachment"].search([("name", "=", "out_test.pdf")])
        assert len(attachment) == 1

    def test_pdf_export(self):
        """The PDF export somehow hides the fields from PyPDF, therefor, we cannot test the content
        of the PDF"""
        self.common_doc_kaamelott.pdf_export(
            {"company_name": "Royaume de Logre"},
            "withholding_tax_certificate_en",
            "wtc_en.pdf",
        )
        attachment = self.env["ir.attachment"].search(
            [("res_id", "=", self.common_doc_kaamelott.id)]
        )
        assert len(attachment) == 1

    def test_amount_in_letter(self):
        self.assertEqual(
            self.common_doc_kaamelott.amount_in_letter(1254.24, "en"),
            "One Thousand, Two Hundred And Fifty-Four Baht and Twenty-Four Satang",
            "Amount in letter should be correct",
        )
