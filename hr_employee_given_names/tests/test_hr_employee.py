from odoo.tests import common
from odoo.exceptions import ValidationError


class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_admin = self.env.ref("hr.employee_admin")

    def test_correct_nickname(self):
        self.employee_admin.given_names = 'Louis Kévin Arnaud Marie'
        self.assertEqual(self.employee_admin.given_names, 'Louis Kévin Arnaud Marie')

    def test_thai_nickname(self):
        self.employee_admin.given_names = 'หลุยส์'
        self.assertEqual(self.employee_admin.given_names, 'หลุยส์')
            