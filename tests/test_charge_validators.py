import unittest

from application import register_utils, charge_validators
from mock import patch

valid_s8 = {
    "charge-type": "dwqdqw",
    "further-information": [
        {
            "information-location": "dwqdwqd:123",
            "references": []
        }
    ],
    "geometry": {
        "crs": {
            "properties": {
                "name": "EPSG:27700"
            },
            "type": "name"
        },
        "coordinates": [
            292225.67273620487,
            92976.9915345409
        ],
        "type": "Point"
    },
    "originating-authorities": [
        "djwioqdqw:12"
    ],
    "statutory-provisions": ["statutory-provision:123"],
    "land-description": "fkfjoekfoe",
    "works-particulars": "fkoekfeofke"
}

valid_s52 = {
    "charge-type": "dwqdqw",
    "further-information": [
        {
            "information-location": "dwqdwqd:123",
            "references": []
        }
    ],
    "geometry": {
        "crs": {
            "properties": {
                "name": "EPSG:27700"
            },
            "type": "name"
        },
        "coordinates": [
            292225.67273620487,
            92976.9915345409
        ],
        "type": "Point"
    },
    "originating-authorities": [
        "djwioqdqw:12"
    ],
    "statutory-provisions": ["statutory-provision:123"],
    "charge-description": "kfeofkeo",
    "capacity-description": "kfoekfoe",
    "compensation-paid": "kfefkeo"
}


class TestChargeValidatorsS8(unittest.TestCase):

    def test_validate_s8_invalid_json_no_statp(self):
        # to quiet flake (need to load register_utils first)
        register_utils.REGISTER_INFO
        self.assertEqual(charge_validators.validate_s8_compensation_charge('local-land-charge', '/', '/', 'post', {}), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_except(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(charge_validators.validate_s8_compensation_charge('local-land-charge', '/', '/', 'post', valid_s8), {'errors': ['an exception']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_none(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = None
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ['Failed to retrieve statutory provision for Land Compensation Act 1973 section 8(4) validation']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_invalid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"vall": "fkoefkoe"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ['Invalid statutory provision for Land Compensation Act 1973 section 8(4) validation']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "Land ComPENsation Act 1973 section 8(4)"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_nots8(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "fneiofjewoif"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ["Charges which conform to land-compensation-charge-s8 definition must contain Land Compensation Act 1973 section 8(4) provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_invalid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "Land ComPENsation Act 1973 section 8(4)"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', {"statutory-provisions": ["statutory-provision:123"]}),
            {'errors': ["Charges with Land Compensation Act 1973 section 8(4) provision must conform to land-compensation-charge-s8 definition"]})


class TestChargeValidatorsS52(unittest.TestCase):

    def test_validate_s52_invalid_json_no_statp(self):
        self.assertEqual(charge_validators.validate_s52_compensation_charge('local-land-charge', '/', '/', 'post', {}), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_except(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(charge_validators.validate_s52_compensation_charge('local-land-charge', '/', '/', 'post', valid_s8), {'errors': ['an exception']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_none(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = None
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ['Failed to retrieve statutory provision for Land Compensation Act 1973 section 52(8) validation']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_invalid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"vall": "fkoefkoe"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ['Invalid statutory provision for Land Compensation Act 1973 section 52(8) validation']})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "Land Compensation Act 1973 section 52(8)"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_nots8(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "fneiofjewoif"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ["Charges which conform to land-compensation-charge-s52 definition must contain Land Compensation Act 1973 section 52(8) provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_invalid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"text": "Land Compensation Act 1973 section 52(8)"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', {"statutory-provisions": ["statutory-provision:123"]}),
            {'errors': ["Charges with Land Compensation Act 1973 section 52(8) provision must conform to land-compensation-charge-s52 definition"]})


class TestChargeValidatorInstrumentProvisions(unittest.TestCase):

    def test_validate_instrument_provisions_istrumentonly(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {"instrument": "mouth organ"}), {'errors': []})

    def test_validate_instrument_provisions_provisionsonly(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {"statutory-provisions": ["mouth organ"]}),
                         {'errors': []})

    def test_validate_instrument_neither(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {}),
                         {'errors': ["At least one of 'statutory-provisions' or 'instrument' must be supplied."]})
