import unittest

from application import register_utils, register_validators


class TestRegisterValidators(unittest.TestCase):

    def test_validate_primary_id_not_put(self):
        # to quiet flake (need to load register_utils first)
        register_utils.REGISTER_INFO
        self.assertEqual(register_validators.validate_primary_id("local-land-charge", "/whatever", "/whatever", 'get', {}), {"errors": []})

    def test_validate_primary_id_no_id(self):
        self.assertEqual(register_validators.validate_primary_id("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {}),
                         {"errors": ["Primary identifier in URI must match key 'local-land-charge' in json"]})

    def test_validate_primary_id_no_match(self):
        self.assertEqual(register_validators.validate_primary_id("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {'local-land-charge': '3'}),
                         {"errors": ["Primary identifier in URI must match key 'local-land-charge' in json"]})

    def test_validate_primary_id_match(self):
        self.assertEqual(register_validators.validate_primary_id("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {'local-land-charge': '1'}),
                         {"errors": []})
