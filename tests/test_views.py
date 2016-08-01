import json
import os
import unittest

from application import app, views
from mock import MagicMock, patch


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status, '200 OK')


class TestException(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = app.test_client()

    def test_exception_catcher(self):
        exception = Exception("An Exception")
        views.internal_exception_handler(exception)
        self.assertEqual(views.internal_exception_handler(exception), ('{"errors": ["An Exception"]}', 500, {'Content-Type': 'application/json'}))


class TestRegisterEndpoints(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = app.test_client()

    def test_get_records_invalid_subdomain(self):
        response = self.app.get('/records')
        self.assertEqual(response.data.decode(), '{"errors": ["invalid sub-domain"]}')

    @patch('application.views.register_utils.register_request')
    def test_get_records_backend_error(self, mock_register_request):
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 400
        mock_response.text = "Some backend error"
        response = self.app.get('/records', headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["Some backend error"]}')

    @patch('application.views.register_utils.register_request')
    def test_get_records_valid(self, mock_register_request):
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = {"a": "thing"}
        response = self.app.get('/records', headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"a": "thing"}')

    def test_get_record_invalid_subdomain(self):
        response = self.app.get('/record/1')
        self.assertEqual(response.data.decode(), '{"errors": ["invalid sub-domain"]}')

    @patch('application.views.register_utils.register_request')
    def test_get_record_backend_error(self, mock_register_request):
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 400
        mock_response.text = "Some backend error"
        response = self.app.get('/record/1', headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["Some backend error"]}')

    @patch('application.views.register_utils.register_request')
    def test_get_record_valid(self, mock_register_request):
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = {"a": "thing"}
        response = self.app.get('/record/1', headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"a": "thing"}')

    @patch('application.views.register_utils.validate_json')
    def test_create_record_validate_json_errors(self, mock_validate_json):
        mock_validate_json.return_value = {"errors": ["an error"]}
        response = self.app.post('/records', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["an error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    def test_create_record_additional_validation_errors(self, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": ["an additional error"]}
        response = self.app.post('/records', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["an additional error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    @patch('application.views.register_utils.register_request')
    def test_create_record_backend_error(self, mock_register_request, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 400
        mock_response.text = "Some backend error"
        response = self.app.post('/records', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["Some backend error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    @patch('application.views.register_utils.register_request')
    def test_create_record_ok(self, mock_register_request, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 201
        mock_response.json.return_value = {"i got": "created", "local-land-charge": "2"}
        response = self.app.post('/records', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"i got": "created", "local-land-charge": "2"}')

    @patch('application.views.register_utils.validate_json')
    def test_update_record_validate_json_errors(self, mock_validate_json):
        mock_validate_json.return_value = {"errors": ["an error"]}
        response = self.app.put('/record/1', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["an error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    def test_update_record_additional_validation_errors(self, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": ["an additional error"]}
        response = self.app.put('/record/1', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["an additional error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    @patch('application.views.register_utils.register_request')
    def test_update_record_backend_error(self, mock_register_request, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 400
        mock_response.text = "Some backend error"
        response = self.app.put('/record/1', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["Some backend error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.additional_validation')
    @patch('application.views.register_utils.register_request')
    def test_update_record_ok(self, mock_register_request, mock_additional_validation, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_additional_validation.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = {"i got": "created", "local-land-charge": "2"}
        response = self.app.put('/record/1', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"i got": "created", "local-land-charge": "2"}')

    def test_geometry_search_invalid_subdomain(self):
        response = self.app.post('/records/geometry/intersects')
        self.assertEqual(response.data.decode(), '{"errors": ["invalid sub-domain"]}')

    def test_geometry_search_nogeo_subdomain(self):
        response = self.app.post('/records/geometry/intersects', headers={"Host": "statutory-provisions.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["invalid sub-domain"]}')

    @patch('application.views.register_utils.validate_json')
    def test_geometry_search_validate_json_errors(self, mock_validate_json):
        mock_validate_json.return_value = {"errors": ["an error"]}
        response = self.app.post('/records/geometry/intersects', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["an error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.register_request')
    def test_geometry_search_backend_error(self, mock_register_request, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 400
        mock_response.text = "Some backend error"
        response = self.app.post('/records/geometry/intersects', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"errors": ["Some backend error"]}')

    @patch('application.views.register_utils.validate_json')
    @patch('application.views.register_utils.register_request')
    def test_geometry_search_ok(self, mock_register_request, mock_validate_json):
        mock_validate_json.return_value = {"errors": []}
        mock_response = MagicMock()
        mock_register_request.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = {"some": "json"}
        response = self.app.post('/records/geometry/intersects', data=json.dumps({"some": "json"}), headers={"Host": "local-land-charge.something.gov"})
        self.assertEqual(response.data.decode(), '{"some": "json"}')
