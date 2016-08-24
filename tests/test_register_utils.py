import unittest
import requests

from application import register_utils
import jsonschema
from mock import patch, MagicMock


class TestRegisterUtilsValidateJson(unittest.TestCase):

    def test_validate_json_invalid_subdomain(self):
        self.assertEqual(register_utils.validate_json('not-a-domain', None, None, None), {"errors": ['invalid sub-domain']})

    def test_validate_json_not_in_raml(self):
        self.assertEqual(register_utils.validate_json('local-land-charge', "/thing", "delete", {}), {"errors": ['cannot find RAML resource definition']})

    def test_validate_json_schema_not_in_raml(self):
        self.assertEqual(register_utils.validate_json('local-land-charge', "/records", "get", {}),
                         {"errors": ['cannot find schema in RAML resource definition']})

    def test_validate_json_valid(self):
        self.assertEqual(register_utils.validate_json('statutory-provision', "/records", "post", {"text": "a provision"}),
                         {"errors": []})

    def test_validate_json_invalid(self):
        self.assertEqual(len(register_utils.validate_json('local-land-charge', "/records", "post", {})['errors']), 19)

    @patch('application.register_utils.jsonschema.Draft4Validator')
    def test_validate_json_schema_invalid(self, mock_validator):
        mock_validator.side_effect = [jsonschema.SchemaError("error")]
        self.assertEqual(register_utils.validate_json(
            'statutory-provision', "/records", "post", {"dumbledore": "a provision"}), {"errors": ['invalid json schema']})


class TestRegisterUtilsAdditionalValidation(unittest.TestCase):

    def test_additional_validation_invalid_subdomain(self):
        self.assertEqual(register_utils.additional_validation('not-a-subdomain', '/records', '/records', 'post', {}),
                         {"errors": ['invalid sub-domain']})

    def test_additional_validation_valid(self):
        self.assertEqual(register_utils.additional_validation('statutory-provision', '/records', '/records', 'post', {}),
                         {"errors": []})


class TestRegisterUtilsRetrieveCurie(unittest.TestCase):

    def setUp(self):
        register_utils.CURIE_CACHE.clear()

    def test_retrieve_curie_invalid_subdomain(self):
        exc = None
        try:
            register_utils.retrieve_curie('not-a-subdomain:1')
        except Exception as e:
            exc = e
        self.assertEqual(str(exc), "Invalid register name 'not-a-subdomain'")

    @patch('application.register_utils.register_request')
    def test_retrieve_curie_404(self, mock_register_request):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_register_request.return_value = mock_response
        self.assertEqual(register_utils.retrieve_curie("local-land-charge:123"), None)

    @patch('application.register_utils.register_request')
    def test_retrieve_curie_200(self, mock_register_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"thing": "ame"}
        mock_register_request.return_value = mock_response
        self.assertEqual(register_utils.retrieve_curie("local-land-charge:123"), {"thing": "ame"})

    @patch('application.register_utils.register_request')
    def test_retrieve_curie_500(self, mock_register_request):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = [Exception("A 500")]
        mock_register_request.return_value = mock_response
        exc = None
        try:
            register_utils.retrieve_curie("local-land-charge:123")
        except Exception as e:
            exc = e
        self.assertEqual(str(exc), "A 500")

    @patch('application.register_utils.register_request')
    def test_retrieve_curie_cache(self, mock_register_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"thing": "ame"}
        mock_register_request.side_effect = [mock_response, None]
        result1 = register_utils.retrieve_curie("local-land-charge:123")
        result2 = register_utils.retrieve_curie("local-land-charge:123")
        self.assertEqual(result1, result2)
        self.assertEqual(result1, {"thing": "ame"})


class TestRegisterUtilsRegisterRequest(unittest.TestCase):

    @patch('application.register_utils.requests.get')
    def test_register_request_exception(self, mock_requests):
        mock_response = MagicMock()
        mock_requests.side_effect = [requests.HTTPError(response=mock_response)]
        mock_response.text = "something like went wrong or something"
        self.assertEqual(register_utils.register_request('a-domain', '/thing', [], 'get', {}), mock_response)

    @patch('application.register_utils.requests.get')
    def test_register_request_exception_doctype(self, mock_requests):
        mock_response = MagicMock()
        mock_requests.side_effect = [requests.HTTPError(response=mock_response)]
        mock_response.text = "<!DOCTYPE HTML whatvkeofkeo"
        exc = None
        try:
            register_utils.register_request('a-domain', '/thing', [], 'get', {})
        except Exception as e:
            exc = e
        self.assertEqual(str(exc), "500: Internal Server Error")

    @patch('application.register_utils.requests.get')
    def test_register_request_ok(self, mock_requests):
        mock_response = MagicMock()
        mock_requests.return_value = mock_response
        self.assertEqual(register_utils.register_request('a-domain', '/thing', [], 'get', {}), mock_response)
