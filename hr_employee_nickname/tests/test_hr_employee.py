from odoo.tests import common, tagged
from odoo.exceptions import ValidationError


@tagged("nickname", "newlogic")
class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_admin = self.env["hr.employee"].create({"name": "Admin"})

    def test_correct_nickname(self):
        self.employee_admin.nickname = "Clovis1er"
        self.assertEqual(self.employee_admin.nickname, "Clovis1er")

    def test_thai_nickname(self):
        self.employee_admin.nickname = "หลุยส์"
        self.assertEqual(self.employee_admin.nickname, "หลุยส์")
