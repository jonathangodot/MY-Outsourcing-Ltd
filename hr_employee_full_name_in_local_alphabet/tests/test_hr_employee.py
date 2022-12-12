from odoo.tests import common, tagged
from odoo.exceptions import ValidationError


@tagged('name_local_alphabet', 'newlogic')
class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_admin = self.env.ref("hr.employee_admin")

    def test_correct_local_name(self):
        self.employee_admin.local_name = 'Clovis'
        self.assertEqual(self.employee_admin.local_name, 'Clovis')
    
    def test_correct_local_name_thai(self):
        self.employee_admin.local_name = 'หลุยส์'
        self.assertEqual(self.employee_admin.local_name, 'หลุยส์')
    
    def test_correct_local_name_thai(self):
        self.employee_admin.local_name = 'लुइस'
        self.assertEqual(self.employee_admin.local_name, 'लुइस')
