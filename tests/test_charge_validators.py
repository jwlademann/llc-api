import unittest

from application import app, register_utils, charge_validators
from mock import patch

LAND_COMP_ACT_S8 = '{} {} {}'.format(app.config['LAND_COMP_ACT_S8_INSTRUMENT'],
                                     app.config['LAND_COMP_ACT_S8_YEAR'],
                                     app.config['LAND_COMP_ACT_S8_PROVISION'])
LAND_COMP_ACT_S52 = '{} {} {}'.format(app.config['LAND_COMP_ACT_S52_INSTRUMENT'],
                                      app.config['LAND_COMP_ACT_S52_YEAR'],
                                      app.config['LAND_COMP_ACT_S52_PROVISION'])

land_compensation_act_s8 = {
    "provision": app.config['LAND_COMP_ACT_S8_PROVISION'],
    "statutory-instrument": app.config['LAND_COMP_ACT_S8_INSTRUMENT'],
    "year": app.config['LAND_COMP_ACT_S8_YEAR']
}

land_compensation_act_s52 = {
    "provision": app.config['LAND_COMP_ACT_S52_PROVISION'],
    "statutory-instrument": app.config['LAND_COMP_ACT_S52_INSTRUMENT'],
    "year": app.config['LAND_COMP_ACT_S52_YEAR']
}

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
    "originating-authority": "djwioqdqw:12",
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
    "originating-authority": "djwioqdqw:12",
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
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {"errors": ["an exception",
                        "Failed to retrieve statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S8 + " validation",
                        "Charges which conform to land-compensation-charge-s8 definition must contain " + LAND_COMP_ACT_S8 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_none(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = None
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ["Failed to retrieve statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S8 + " validation",
                        "Charges which conform to land-compensation-charge-s8 definition must contain " + LAND_COMP_ACT_S8 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_invalid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"vall": "fkoefkoe"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ["Invalid statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S8 + " validation",
                        "Charges which conform to land-compensation-charge-s8 definition must contain " + LAND_COMP_ACT_S8 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = land_compensation_act_s8
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_valid_json_statp_nots8(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900"}
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ["Charges which conform to land-compensation-charge-s8 definition must contain " + LAND_COMP_ACT_S8 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s8_invalid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = land_compensation_act_s8
        self.assertEqual(charge_validators.validate_s8_compensation_charge(
            'local-land-charge', '/', '/', 'post', {"statutory-provisions": ["statutory-provision:123"]}),
            {'errors': ["Charges with " + LAND_COMP_ACT_S8 + " provision must conform to land-compensation-charge-s8 definition"]})


class TestChargeValidatorsS52(unittest.TestCase):

    def test_validate_s52_invalid_json_no_statp(self):
        self.assertEqual(charge_validators.validate_s52_compensation_charge('local-land-charge', '/', '/', 'post', {}), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_except(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s8),
            {'errors': ['an exception',
                        "Failed to retrieve statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S52 + " validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_none(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = None
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ["Failed to retrieve statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S52 + " validation",
                        "Charges which conform to land-compensation-charge-s52 definition must contain " + LAND_COMP_ACT_S52 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_invalid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"vall": "fkoefkoe"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ["Invalid statutory provision 'statutory-provision:123' for " + LAND_COMP_ACT_S52 + " validation",
                        "Charges which conform to land-compensation-charge-s52 definition must contain " + LAND_COMP_ACT_S52 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = land_compensation_act_s52
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52), {'errors': []})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_valid_json_statp_nots8(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"provision": "section 1",
                                            "statutory-instrument": "a provision",
                                            "year": "1066"}
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', valid_s52),
            {'errors': ["Charges which conform to land-compensation-charge-s52 definition must contain " + LAND_COMP_ACT_S52 + " provision"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_s52_invalid_json_statp_valid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = land_compensation_act_s52
        self.assertEqual(charge_validators.validate_s52_compensation_charge(
            'local-land-charge', '/', '/', 'post', {"statutory-provisions": ["statutory-provision:123"]}),
            {'errors': ["Charges with " + LAND_COMP_ACT_S52 + " provision must conform to land-compensation-charge-s52 definition"]})


class TestChargeValidatorInstrumentProvisions(unittest.TestCase):

    def test_validate_instrument_provisions_instrumentonly(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {"instrument": "mouth organ"}), {'errors': []})

    def test_validate_instrument_provisions_provisionsonly(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {"statutory-provisions": ["mouth organ"]}),
                         {'errors': []})

    def test_validate_instrument_neither(self):
        self.assertEqual(charge_validators.validate_instrument_provisions("blah", "blah", "blah", "blah", {}),
                         {'errors': ["At least one of 'statutory-provisions' or 'instrument' must be supplied."]})


class TestValidateStatutoryProvisions(unittest.TestCase):

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_exception(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "blah", "blah", "blah", "blah", {"statutory-provisions": ["statutory-provision:321"]}),
            {'errors': ['an exception',
                        "Failed to retrieve statutory provision 'statutory-provision:321' for statutory provision validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_notext(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"no-text": "field"}
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "blah", "blah", "blah", "blah", {"statutory-provisions": ["statutory-provision:321"]}),
            {'errors': ["Invalid statutory provision 'statutory-provision:321' for statutory provision validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_archived_post(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900", "end-date": "something"}
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "blah", "blah", "blah", "post", {"statutory-provisions": ["statutory-provision:321"]}),
            {'errors': ["New charges cannot use archived statutory provision 'statutory-provision:321'"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_archived_put_exception(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [{"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900",
                                            "end-date": "something"},
                                           Exception("an exception")]
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "local-land-charge", "blah", "blah", "put", {"statutory-provisions": ["statutory-provision:321"], "local-land-charge": "2"}),
            {'errors': ['an exception', "Could not retrieve record 'local-land-charge:2' for statutory provision validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_archived_put_archived(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [{"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900", "end-date": "something"},
                                           {"statutory-provisions": ["statutory-provision:321"], "local-land-charge": "2"}]
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "local-land-charge", "blah", "blah", "put", {"statutory-provisions": ["statutory-provision:123"], "local-land-charge": "2"}),
            {'errors': ["Cannot add archived statutory provision 'statutory-provision:123'"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_statutory_provisions_archived_put_ok(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [{"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900",
                                            "end-date": "something"},
                                           {"statutory-provisions": ["statutory-provision:321"], "local-land-charge": "2"},
                                           {"provision": "section",
                                            "statutory-instrument": "Act",
                                            "year": "1900"}]
        self.assertEqual(charge_validators.validate_statutory_provisions(
            "local-land-charge", "blah", "blah", "put", {"statutory-provisions": ["statutory-provision:321", "statutory-provision:123"],
                                                         "local-land-charge": "2"}),
                         {'errors': []})


class TestValidateRegistrationDate(unittest.TestCase):

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_registration_date_nodate_except(self, mock_curie_retrieve):
        mock_curie_retrieve.side_effect = [Exception("an exception")]
        self.assertEqual(charge_validators.validate_registration_date(
            'local-land-charge', 'blah', 'blah', 'put', {"local-land-charge": "1"}),
            {'errors': ['an exception', "Could not retrieve record 'local-land-charge:1' for update validation"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_registration_date_nodate_invalid(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"local-land-charge": "1"}
        self.assertEqual(charge_validators.validate_registration_date(
            'local-land-charge', 'blah', 'blah', 'put', {"local-land-charge": "1"}),
            {'errors': ["Existing record has no 'registration-date', cannot update"]})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_registration_date_nodate_ok(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"local-land-charge": "1", "registration-date": "something"}
        json = {"local-land-charge": "1"}
        self.assertEqual(charge_validators.validate_registration_date(
            'local-land-charge', 'blah', 'blah', 'put', json),
            {'errors': []})
        self.assertEqual(json, {"local-land-charge": "1", "registration-date": "something"})

    @patch('application.charge_validators.register_utils.retrieve_curie')
    def test_validate_registration_date_date_change(self, mock_curie_retrieve):
        mock_curie_retrieve.return_value = {"local-land-charge": "1", "registration-date": "something"}
        json = {"local-land-charge": "1", "registration-date": "something else"}
        self.assertEqual(charge_validators.validate_registration_date(
            'local-land-charge', 'blah', 'blah', 'put', json),
            {'errors': ["Cannot update field 'registration-date'"]})


class TestValidateFurtherInformation(unittest.TestCase):

    def test_validate_further_information_dupe(self):
        json = {"local-land-charge": "1", "further-information": [{"information-location": "dwqdwqd:123", "references": []},
                                                                  {"information-location": "dwqdwqd:123", "references": ["areference"]}]}
        self.assertEqual(charge_validators.validate_further_information(
            'local-land-charge', 'blah', 'blah', 'put', json),
            {'errors': ['Further information locations must be unique']})

    def test_validate_further_information_ok(self):
        json = {"local-land-charge": "1", "further-information": [{"information-location": "dwqdwqd:123", "references": []},
                                                                  {"information-location": "dwqdwhqd:123", "references": ["areference"]}]}
        self.assertEqual(charge_validators.validate_further_information(
            'local-land-charge', 'blah', 'blah', 'put', json),
            {'errors': []})
