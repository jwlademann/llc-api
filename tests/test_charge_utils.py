import json
import os
import unittest

import requests
import werkzeug

from application import charge_utils
from application.views import app
import mock


class FakeResponse(requests.Response):

    def __init__(self, content='', status_code=200):
        super(FakeResponse, self).__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code


class TestChargeUtils(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = app.test_client()

    def test_validate_json_invalid_sub_domain(self):
        request_json = None
        sub_domain = "invalid"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertEqual(result['errors'][0], "invalid sub-domain")

    def test_validate_geometry_search_json(self):
        request_json = {"geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method, search=True)
        self.assertEqual(len(result['errors']), 0)

    @mock.patch('application.charge_utils.validate_statutory_provisions')
    def test_validate_json_missing_field(self, mock_validate_stat_prov):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"]}
        mock_validate_stat_prov.return_value = None
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertTrue("'geometry' is a required property" in result['errors'][0])

    def test_validate_json_missing_extra_field_on_update(self):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'PUT'
        primary_id = 1
        result = charge_utils.validate_json(request_json, sub_domain, request_method, primary_id)
        self.assertIn("'local-land-charge' is a required property", str(result['errors']))

    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_json_blank_inspection_reference(self, mock_get):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123"}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_get.return_value = (provision_not_land_comp, 200)
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertEqual(len(result['errors']), 0)

    def test_validate_json_missing_place_of_inspection(self):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertIn("'further-information' is a required property", str(result['errors']))

    def test_validate_json_invalid_field_type(self):
        request_json = {"local-land-charge": 1,
                        "charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'PUT'
        primary_id = 1
        result = charge_utils.validate_json(request_json, sub_domain, request_method, primary_id)
        self.assertIn("1 is not of type 'string'", str(result['errors']))

    def test_validate_json_primary_id_does_not_match_url(self):
        request_json = {"local-land-charge": "2",
                        "charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'PUT'
        primary_id = 1
        result = charge_utils.validate_json(request_json, sub_domain, request_method, primary_id)
        self.assertIn("'2' does not match '1'", str(result['errors']))

    def test_validate_json_remove_invalid_fields(self):
        request_json = {"fruit": "banana",
                        "charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertIn("Additional properties are not allowed ('fruit' was unexpected)", str(result['errors']))

    def test_validate_invalid_curies(self):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test-321"],
                        "charge-description": "test",
                        "originating-authorities": ["test-123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertIn(" 'statutory-provisions' must be specified as a Curie", str(result['errors']))
        self.assertIn(" 'originating-authorities' must be specified as a Curie", str(result['errors']))

    def test_validate_json_whitespace_value(self):
        request_json = {"charge-type": "    ",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test"}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertIn("'charge-type' must not be blank", str(result['errors']))

    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_json_valid_json(self, mock_get):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_get.return_value = (provision_not_land_comp, 200)
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertEqual(len(result['errors']), 0)

    def test_remove_empty_array_values(self):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321", "", ""],
                        "charge-description": "test",
                        "originating-authorities": ["", "test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}

        charge_utils.remove_empty_array_values(request_json)
        self.assertEqual(request_json["statutory-provisions"], ["test:321"])
        self.assertEqual(request_json["originating-authorities"], ["test:123"])

    def test_validate_json_invalid_date(self):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "creation-date": "29/02/2008",
                        "expiration-date": "29/02/2009",
                        "further-information": [{"information-location": "test"}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        self.assertIn("'expiration-date' is an invalid date", str(result['errors']))

    # @mock.patch('application.charge_utils.validate_statutory_provisions')
    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_json_valid_json_with_optional_fields(self, mock_get):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"},
                        "creation-date": "2016-01-01",
                        "expiration-date": "2016-02-02",
                        "instrument": "test",
                        "migrating-authority": "test",
                        "old-register-part": "1",
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["test"]}],
                        "unique-property-reference-numbers": [1234]
                        }
        # mock_validate_stat_prov.return_value = None
        mock_get.return_value = (provision_not_land_comp, 200)
        sub_domain = "local-land-charge"
        request_method = 'POST'
        result = charge_utils.validate_json(request_json, sub_domain, request_method)
        print(result['errors'])
        self.assertEqual(len(result['errors']), 0)

    def test_process_update_request_invalid_sub_domain(self):
        host_url = "invalid.landregistry.gov.uk"
        request_method = 'POST'
        request_json = None
        result = charge_utils.process_update_request(host_url, request_method, request_json)
        self.assertEqual(json.loads(result[0])['errors'][0], "invalid sub-domain")

    @mock.patch('application.charge_utils.requests.post', side_effect=requests.ConnectionError())
    def test_process_update_request_connection_error(self, mock_post):
        host_url = "local-land-charge.landregistry.gov.uk"
        request_method = 'POST'
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"},
                                             "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}
                        }
        try:
            charge_utils.process_update_request(host_url, request_method, request_json)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    @mock.patch('application.charge_utils.requests.post')
    def test_process_update_request_http_error(self, mock_post):
        mock_post.side_effect = requests.HTTPError()
        mock_post.side_effect.response = FakeResponse(str.encode("This is an error message"),
                                                      status_code=404)
        host_url = "local-land-charge.landregistry.gov.uk"
        request_method = 'POST'
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"},
                                             "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}
                        }
        result = charge_utils.process_update_request(host_url, request_method, request_json)
        self.assertEqual(result[1], 404)

    @mock.patch('application.charge_utils.requests.post')
    def test_process_update_request_http_error_html_content(self, mock_post):
        mock_post.side_effect = requests.HTTPError()
        mock_post.side_effect.response = FakeResponse(str.encode("<!DOCTYPE HTML"),
                                                      status_code=404)
        host_url = "local-land-charge.landregistry.gov.uk"
        request_method = 'POST'
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"},
                                             "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}
                        }
        try:
            charge_utils.process_update_request(host_url, request_method, request_json)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    @mock.patch('application.charge_utils.requests.post')
    def test_process_update_request_valid_post(self, mock_post):
        mock_post.return_value = FakeResponse(str.encode(json.dumps(post_response)),
                                              status_code=201)
        host_url = "local-land-charge.landregistry.gov.uk"
        request_method = 'POST'
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"},
                                             "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}
                        }
        result = charge_utils.process_update_request(host_url, request_method, request_json, resolve='1')
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0])['record']['charge-type'],
                         request_json['charge-type'])
        self.assertEqual(json.loads(result[0])['href'], host_url + "/record/48")

    @mock.patch('application.charge_utils.requests.put')
    def test_process_update_request_valid_put(self, mock_put):
        mock_put.return_value = FakeResponse(str.encode(json.dumps(post_response)),
                                             status_code=201)
        host_url = "local-land-charge.landregistry.gov.uk"
        request_method = 'PUT'
        request_json = {"local-land-charge": "48",
                        "charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"},
                                             "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}
                        }
        primary_id = '48'
        result = charge_utils.process_update_request(host_url, request_method, request_json,
                                                     primary_id=primary_id, resolve='1')
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0])['record']['charge-type'],
                         request_json['charge-type'])
        self.assertEqual(json.loads(result[0])['href'], host_url + "/record/48")

    def test_process_get_request_invalid_sub_domain(self):
        host_url = "invalid.landregistry.gov.uk"
        result = charge_utils.process_get_request(host_url)
        self.assertEqual(json.loads(result[0])['errors'][0], "invalid sub-domain")

    @mock.patch('application.charge_utils.requests.get', side_effect=requests.ConnectionError())
    def test_process_get_request_connection_error(self, mock_get):
        host_url = "local-land-charge.landregistry.gov.uk"
        try:
            charge_utils.process_get_request(host_url)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    @mock.patch('application.charge_utils.requests.get')
    def test_process_get_request_http_error(self, mock_get):
        mock_get.side_effect = requests.HTTPError()
        mock_get.side_effect.response = FakeResponse(str.encode("This is an error message"),
                                                     status_code=404)
        host_url = "local-land-charge.landregistry.gov.uk"
        result = charge_utils.process_get_request(host_url)
        self.assertEqual(result[1], 404)

    @mock.patch('application.charge_utils.requests.get')
    def test_process_get_request_http_error_html_content(self, mock_get):
        mock_get.side_effect = requests.HTTPError()
        mock_get.side_effect.response = FakeResponse(str.encode("<!DOCTYPE HTML"),
                                                     status_code=404)
        host_url = "local-land-charge.landregistry.gov.uk"
        try:
            charge_utils.process_get_request(host_url)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    @mock.patch('application.charge_utils.requests.get')
    def test_process_get_request_valid_get(self, mock_get):
        mock_get.return_value = FakeResponse(str.encode(json.dumps(get_response_many)),
                                             status_code=201)
        host_url = "local-land-charge.landregistry.gov.uk"
        result = charge_utils.process_get_request(host_url)
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0]), get_response_many)

    @mock.patch('application.charge_utils.requests.get')
    def test_process_get_request_valid_get_with_primary_id(self, mock_get):
        mock_get.return_value = FakeResponse(str.encode(json.dumps(get_response_one)), status_code=201)
        host_url = "local-land-charge.landregistry.gov.uk"
        primary_id = '3'
        result = charge_utils.process_get_request(host_url, primary_id=primary_id)
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0])['charge-type'], "test")

    @mock.patch('application.charge_utils.requests.get')
    def test_get_request_resolve(self, mock_get):
        mock_get.return_value = FakeResponse(str.encode(json.dumps(get_response_one)), status_code=201)
        host_url = "local-land-charge.landregistry.gov.uk"
        primary_id = '3'
        result = charge_utils.process_get_request(host_url, primary_id=primary_id, resolve="1")
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0])['charge-type'], "test")

    @mock.patch('application.charge_utils.validate_statutory_provisions')
    def test_validate_multiple_compensation_provisions_invalid(self, mock_validate_stat_prov):
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321", "statutory-provision:987"],
                        "originating-authorities": ["test:123"],
                        "land-description": "land",
                        "works-particulars": "particulars",
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_stat_prov.return_value = ("Land-Compensation-Charge-S8")
        sub_domain = "local-land-charge"
        request_method = 'POST'
        primary_id = 1
        search = False
        result = charge_utils.validate_helper(request_json, sub_domain, request_method, primary_id, search)
        print(result)
        self.assertEqual(len(result), 1)
        self.assertIn("Problem 1: 'statutory-provisions' ['statutory-provision:321', 'statutory-provision:987'] is too long", result[0])

    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_compensation_act_section8(self, mock_get):
        errors = []
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_get.return_value = (provision_land_comp_section8, 200)
        result = charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(result, 'Land-Compensation-Charge-S8')    \

    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_compensation_act_section52(self, mock_get):
        errors = []
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_get.return_value = (provision_land_comp_section_52, 200)
        result = charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(result, 'Land-Compensation-Charge-S52')

    def test_validate_statutory_provision_schema(self):
        compensation_charge = None
        sub_domain = 'statutory-provision'
        search = False
        result = charge_utils.load_json_schema(compensation_charge, sub_domain, search)
        print(result)
        self.assertEqual(result, 0)


    @mock.patch('application.charge_utils.process_get_request')
    def test_validate_provisions_not_found(self, mock_get):
        errors = []
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision:321", "statutory-provision:987"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_get.return_value = (provision_land_comp_section8, 404)
        charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(len(errors), 2)
        self.assertIn("Could not find record in statutory-provision", errors[0])
        self.assertIn("Could not find record in statutory-provision", errors[1])

    def test_validate_provisions_no_instrument(self):
        errors = []
        request_json = {"charge-type": "test",
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(len(errors), 1)
        self.assertIn("At least one of 'statutory-provisions' or 'instrument' must be supplied", errors[0])

    def test_validate_provisions_invalid_register(self):
        errors = []
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["test:321"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid register provided", errors[0])

    def test_validate_provisions_index_error(self):
        errors = []
        request_json = {"charge-type": "test",
                        "statutory-provisions": ["statutory-provision"],
                        "charge-description": "test",
                        "originating-authorities": ["test:123"],
                        "further-information": [{"information-location": "test:123",
                                                 "references": ["qwerty"]}],
                        "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                                     "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                                      [257661.0, 62362.0], [241959.0, 62362.0],
                                                      [241959.0, 52874.0]]], "type": "Polygon"}}
        charge_utils.validate_statutory_provisions(errors, request_json)
        self.assertEqual(len(errors), 1)
        self.assertIn("No ID supplied", errors[0])

    @mock.patch('application.charge_utils.requests.post')
    def test_process_geometry_search(self, mock_post):
        mock_post.return_value = FakeResponse(str.encode(json.dumps(search_result_many)), status_code=201)
        request_json = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        host_url = "local-land-charge.landregistry.gov.uk"
        result = charge_utils.process_geometry_search(host_url, request_json)
        self.assertEqual(result[1], 201)
        self.assertEqual(json.loads(result[0]), search_result_many)

    @mock.patch('application.charge_utils.requests.post')
    def test_process_geometry_search_http_error(self, mock_post):
        mock_post.side_effect = requests.HTTPError()
        mock_post.side_effect.response = FakeResponse(str.encode("This is an error message"), status_code=404)
        request_json = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        host_url = "local-land-charge.landregistry.gov.uk"
        result = charge_utils.process_geometry_search(host_url, request_json)
        self.assertEqual(result[1], 404)

    @mock.patch('application.charge_utils.requests.post')
    def test_process_geometry_search_http_error_html_content(self, mock_post):
        mock_post.side_effect = requests.HTTPError()
        mock_post.side_effect.response = FakeResponse(str.encode("<!DOCTYPE HTML"), status_code=404)
        request_json = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        host_url = "local-land-charge.landregistry.gov.uk"
        try:
            charge_utils.process_geometry_search(host_url, request_json)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    @mock.patch('application.charge_utils.requests.post', side_effect=requests.ConnectionError())
    def test_process_geometry_search_connection_error(self, mock_post):
        host_url = "local-land-charge.landregistry.gov.uk"
        request_json = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        try:
            charge_utils.process_geometry_search(host_url, request_json)
            self.fail('exception expected.')
        except werkzeug.exceptions.HTTPException as e:
            self.assertEqual(e.get_response().status_code, 500)

    def test_process_geometry_search_invalid_sub_domain(self):
        host_url = "invalid.landregistry.gov.uk"
        request_json = None
        result = charge_utils.process_geometry_search(host_url, request_json)
        self.assertEqual(json.loads(result[0])['errors'][0], "invalid sub-domain")

post_response = {
    "charge-type": "test",
    "charge-description": "test",
    "entry-number": "53",
    "entry-timestamp": "2016-05-19T10:58:27.568286",
    "geometry": {
        "coordinates": [
            [
                [
                    423125.59,
                    211640.34
                ],
                [
                    423098.61,
                    211586.64
                ],
                [
                    423136.82,
                    211540.82
                ],
                [
                    423150.57,
                    211597.37
                ],
                [
                    423125.59,
                    211640.34
                ]
            ]
        ],
        "crs": {
            "properties": {
                "name": "EPSG:27700"
            },
            "type": "name"
        },
        "type": "Polygon"
    },
    "item-hash": "sha-256:19acd35ddf2b64bb8f3840bdcb54bc6bc9d3a1eb1c42a60c63cbbc3de6a3dc1e",
    "local-land-charge": "48",
    "originating-authorities": "test:123",
    "provision": "test:123"
}

get_response_many = [
    {
        "charge-type": "test",
        "charge-description": "test",
        "entry-number": "3",
        "entry-timestamp": "2016-05-16T16:20:51.279816",
        "geometry": {
            "coordinates": [
                [
                    [
                        423125.59,
                        211640.34
                    ],
                    [
                        423098.61,
                        211586.64
                    ],
                    [
                        423136.82,
                        211540.82
                    ],
                    [
                        423150.57,
                        211597.37
                    ],
                    [
                        423125.59,
                        211640.34
                    ]
                ]
            ],
            "crs": {
                "properties": {
                    "name": "EPSG:27700"
                },
                "type": "name"
            },
            "type": "Polygon"
        },
        "item-hash": "sha-256:34c70397dcd1d85af72203a9804951dcaaf09cb3800f3a4009da07dc7c044e4f",
        "local-land-charge": "2",
        "originating-authorities": "test:123",
        "provision": "test:123"
    },
    {
        "charge-type": "test",
        "charge-description": "test",
        "entry-number": "4",
        "entry-timestamp": "2016-05-16T16:20:55.848333",
        "geometry": {
            "coordinates": [
                [
                    [
                        423125.59,
                        211640.34
                    ],
                    [
                        423098.61,
                        211586.64
                    ],
                    [
                        423136.82,
                        211540.82
                    ],
                    [
                        423150.57,
                        211597.37
                    ],
                    [
                        423125.59,
                        211640.34
                    ]
                ]
            ],
            "crs": {
                "properties": {
                    "name": "EPSG:27700"
                },
                "type": "name"
            },
            "type": "Polygon"
        },
        "item-hash": "sha-256:b76d8fd679d335efee91b80bfb13871e77ec4f9e791a3875edd4fdce2bc1c593",
        "local-land-charge": "3",
        "originating-authorities": "test:123",
        "provision": "test:123"
    }
]


get_response_one = {
    "charge-type": "test",
    "charge-description": "test",
    "entry-number": "4",
    "entry-timestamp": "2016-05-16T16:20:55.848333",
    "geometry": {
        "coordinates": [
            [
                [
                    423125.59,
                    211640.34
                ],
                [
                    423098.61,
                    211586.64
                ],
                [
                    423136.82,
                    211540.82
                ],
                [
                    423150.57,
                    211597.37
                ],
                [
                    423125.59,
                    211640.34
                ]
            ]
        ],
        "crs": {
            "properties": {
                "name": "EPSG:27700"
            },
            "type": "name"
        },
        "type": "Polygon"
    },
    "item-hash": "sha-256:b76d8fd679d335efee91b80bfb13871e77ec4f9e791a3875edd4fdce2bc1c593",
    "local-land-charge": "3",
    "originating-authorities": "test:123",
    "provision": "test:123"
}

provision_land_comp_section8 = '{"entry-number": "1", "entry-timestamp": "2016-06-23T10:44:22.515174", ' \
                      '"item-hash": "sha-256:cc53bb1ec3cc2facbdf4f3f064e08fbd2620a3452f16ee2723a030cded15cbe3", ' \
                      '"statutory-provision": "1", "text": "Land Compensation Act 1973 s.8(4)"}'

provision_land_comp_section_52 = '{"entry-number": "1", "entry-timestamp": "2016-06-23T10:44:22.515174", ' \
                                 '"item-hash": "sha-256:cc53bb1ec3cc2facbdf4f3f064e08fbd2620a3452f16ee2723a030cded15cbe3", ' \
                                 '"statutory-provision": "1", "text": "Land Compensation Act 1973 s.52(8)"}'

provision_not_land_comp = '{"entry-number": "2", "entry-timestamp": "2016-06-23T10:48:49.603961",' \
                          ' "item-hash": "sha-256:d68d21babfda2646b1516e70e047ded0555b76275937f18371458067f28ed687", ' \
                          '"statutory-provision": "2", "text": "Something else"}'

search_result_many = {
  "3202": {
    "charge-type": "type c",
    "description": "Plot 196",
    "entry-number": "3202",
    "entry-timestamp": "2016-06-21T10:25:03.902929",
    "further-information": [
      {
        "information-location": "further-information-location:5",
        "references": [
          "PLA/196"
        ]
      }
    ],
    "geometry": {
      "coordinates": [
        [
          [
            293518.5,
            91099.2
          ],
          [
            293785.0,
            91099.2
          ],
          [
            293785.0,
            91267.4
          ],
          [
            293518.5,
            91267.4
          ],
          [
            293518.5,
            91099.2
          ]
        ]
      ],
      "crs": {
        "properties": {
          "name": "EPSG:27700"
        },
        "type": "name"
      },
      "type": "Polygon"
    },
    "instrument": "Deed",
    "item-hash": "sha-256:f21568f065862a93e19d0f7ebc9baa0da6240e104a830175fce752d043444f00",
    "local-land-charge": "3202",
    "originating-authority": "llc-registering-authority:5",
    "provision": "statutory-provision:665"
  },
  "3932": {
    "charge-type": "type d",
    "description": "Plot 926",
    "entry-number": "3932",
    "entry-timestamp": "2016-06-21T10:25:13.849768",
    "further-information": [
      {
        "information-location": "further-information-location:5",
        "references": [
          "PLA/926"
        ]
      }
    ],
    "geometry": {
      "coordinates": [
        [
          [
            293518.5,
            91099.2
          ],
          [
            294318.0,
            91099.2
          ],
          [
            294318.0,
            91603.8
          ],
          [
            293518.5,
            91603.8
          ],
          [
            293518.5,
            91099.2
          ]
        ]
      ],
      "crs": {
        "properties": {
          "name": "EPSG:27700"
        },
        "type": "name"
      },
      "type": "Polygon"
    },
    "instrument": "Deed",
    "item-hash": "sha-256:c6665f4d48e220b0ed65f393289014666733b99e6f5161192f51aa563a7d4372",
    "local-land-charge": "3932",
    "originating-authority": "llc-registering-authority:5",
    "provision": "statutory-provision:689"
  }
}
