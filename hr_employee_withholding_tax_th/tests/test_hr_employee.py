from odoo.tests import common, tagged
from odoo.exceptions import ValidationError

# import logging
# _logger = logging.getLogger(__name__)


# @tagged('fields_withholding_thailand', 'newlogic')
class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee = self.env['hr.employee'].create({'name': 'Karadok'})
    
    def test_check_int_fields(self):
        self.employee.parents_allowance = 1
        self.assertEqual(self.employee.parents_allowance, 1)

        try:
            self.employee.parents_allowance = -1
        except ValidationError:
            assert True
        
        try:
            self.employee.parents_allowance = 0.5
        except ValidationError:
            assert True
        
        try:
            self.employee.parents_allowance = 'value'
        except ValueError:
            True
        
        """TODO : Complete test suite for other int fields"""

    def test_check_float_fields(self):
        self.employee.ssf = 10000.0
        self.assertEqual(self.employee.ssf, 10000.0)

        try:
            self.employee.ssf = -10000
        except ValidationError:
            assert True
        
        try:
            self.employee.ssf = 'value'
        except ValueError:
            assert True

        """TODO : Complete test suite for other float fields"""
