import unittest

from application import register_utils, register_validators
from mock import patch


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

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_archive_update_except(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(register_validators.validate_archive_update("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {'local-land-charge': '1'}),
                         {'errors': ['an exception', "Could not retrieve record 'local-land-charge:1' for update validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_archive_update_archived(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {'local-land-charge': '3', 'end-date': 'something'}
        self.assertEqual(register_validators.validate_archive_update("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {'local-land-charge': '1'}),
                         {'errors': ['Record has been archived, cannot update']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_archive_update_notarchived(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {'local-land-charge': '3'}
        self.assertEqual(register_validators.validate_archive_update("local-land-charge", "/whatever/1", "/whatever/{dwdw}", 'put', {'local-land-charge': '1'}),
                         {'errors': []})
