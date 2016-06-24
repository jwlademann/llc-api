from application.views import app
import json
import mock
import os
import requests
import unittest


class FakeResponse(requests.Response):
    def __init__(self, content='', status_code=200):
        super(FakeResponse, self).__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code


class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status, '200 OK')

    def test_get_charges_invalid_sub_domain(self):
        response = self.app.get('/records')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], 'invalid sub-domain')

    @mock.patch('application.charge_utils.process_get_request')
    def test_get_charges_success(self, mock_get):
        mock_get.return_value = (json.dumps(get_response_many), 200,
                                 {"Content-Type": "application/json"})
        response = self.app.get('/records', headers={"Host": "local-land-charge.my_url.gov.uk"})
        # response = self.app.get('/records')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json, get_response_many)

    def test_get_charge_invalid_sub_domain(self):
        primary_id = "3"
        response = self.app.get('/record/' + primary_id)
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], 'invalid sub-domain')

    @mock.patch('application.charge_utils.process_get_request')
    def test_get_charge_success(self, mock_process_get_request):
        mock_process_get_request.return_value = (json.dumps(get_response_one), 200,
                                                 {"Content-Type": "application/json"})
        primary_id = "3"
        response = self.app.get('/record/' + primary_id,
                                headers={"Host": "local-land-charge.my_url.gov.uk"})
        # response = self.app.get('/records')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json, get_response_one)

    def test_create_charge_invalid_sub_domain(self):
        response = self.app.post('/records')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], 'invalid sub-domain')

    @mock.patch('application.charge_utils.validate_json')
    def test_create_charge_validation_fail(self, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test"}
        mock_validate_json.return_value = {"errors": ["'geometry' is a required property"]}
        response = self.app.post('/records', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk", "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "'geometry' is a required property")

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_update_request')
    def test_create_charge_register_validation_fail(self, mock_update_request, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                             "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0], [257661.0, 62362.0],
                                              [241959.0, 62362.0], [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_json.return_value = {"errors": []}
        mock_update_request.return_value = (
            json.dumps({"errors": ["register validation error"]}),
            400, {"Content-Type": "application/json"}
        )

        response = self.app.post('/records', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk",
                                          "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "register validation error")

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_update_request')
    def test_create_charge_success(self, mock_update_request, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                             "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                              [257661.0, 62362.0], [241959.0, 62362.0],
                                              [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_json.return_value = {"errors": []}
        mock_update_request.return_value = (
            json.dumps({"href": "local-land-charge.my_url.gov.uk/record/" +
                                post_response['local-land-charge'],
                        "record": post_response}),
            201, {"Content-Type": "application/json"}
        )

        response = self.app.post('/records', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk", "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['href'], "local-land-charge.my_url.gov.uk/record/48")
        self.assertEqual(response_json['record'], post_response)

    def test_update_charge_invalid_sub_domain(self):
        response = self.app.put('/record/48')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], 'invalid sub-domain')

    @mock.patch('application.charge_utils.validate_json')
    def test_update_charge_validation_fail(self, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                             "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                              [257661.0, 62362.0], [241959.0, 62362.0],
                                              [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_json.return_value = {"errors": ["'local-land-charge' is a required property"]}
        response = self.app.put('/record/48', data=json.dumps(data),
                                headers={"Host": "local-land-charge.my_url.gov.uk", "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "'local-land-charge' is a required property")

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_update_request')
    def test_update_charge_register_validation_fail(self, mock_update_request, mock_validate_json):
        data = {"local-land-charge": "48",
                "charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                             "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                              [257661.0, 62362.0], [241959.0, 62362.0],
                                              [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_json.return_value = {"errors": []}
        mock_update_request.return_value = (
            json.dumps({"errors": ["register validation error"]}),
            400, {"Content-Type": "application/json"}
        )

        response = self.app.put('/record/48', data=json.dumps(data),
                                headers={"Host": "local-land-charge.my_url.gov.uk", "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "register validation error")

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_update_request')
    def test_update_charge_success(self, mock_update_request, mock_validate_json):
        data = {"local-land-charge": "48",
                "charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": {"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"},
                             "coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0],
                                              [257661.0, 62362.0], [241959.0, 62362.0],
                                              [241959.0, 52874.0]]], "type": "Polygon"}}
        mock_validate_json.return_value = {"errors": []}
        mock_update_request.return_value = (
            json.dumps({"href": "local-land-charge.my_url.gov.uk/record/" +
                                post_response['local-land-charge'],
                        "record": post_response}),
            201, {"Content-Type": "application/json"}
        )

        response = self.app.put('/record/48', data=json.dumps(data),
                                headers={"Host": "local-land-charge.my_url.gov.uk", "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['href'], "local-land-charge.my_url.gov.uk/record/48")
        self.assertEqual(response_json['record'], post_response)

    @mock.patch('application.views.charge_utils.validate_json')
    def test_create_charge_exception(self, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": 123}
        mock_validate_json.return_value = {"errors": ['geometry is not of type object']}

        response = self.app.post('/records', data=json.dumps(data), headers={"Host": "local-land-charge.my_url.gov.uk",
                                                                             "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "geometry is not of type object")

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_update_request')
    def test_create_charge_valid_geometry_string(self, mock_update_request, mock_validate_json):
        data = {"charge-type": "test",
                "provision": "test",
                "description": "test",
                "originating-authority": "test",
                "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
                            '"coordinates": [[[241959.0, 52874.0], [257661.0, 52874.0], [257661.0, 62362.0], '
                            '[241959.0, 62362.0], [241959.0, 52874.0]]], "type": "Polygon"}'}
        mock_validate_json.return_value = {"errors": []}
        mock_update_request.return_value = (
            json.dumps({"href": "local-land-charge.my_url.gov.uk/record/" +
                                post_response['local-land-charge'],
                        "record": post_response}),
            201, {"Content-Type": "application/json"}
        )

        response = self.app.post('/records', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk",
                                          "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['href'], "local-land-charge.my_url.gov.uk/record/48")
        self.assertEqual(response_json['record'], post_response)

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_geometry_search')
    def test_geometry_search_success(self, mock_process_geometry_search, mock_validate_json):
        data = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        mock_validate_json.return_value = {"errors": []}
        mock_process_geometry_search.return_value = (
            json.dumps(search_result_many),
            201, {"Content-Type": "application/json"}
        )

        response = self.app.post('/records/geometry/intersect', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk",
                                          "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json, search_result_many)

    @mock.patch('application.charge_utils.validate_json')
    @mock.patch('application.charge_utils.process_geometry_search')
    def test_geometry_search_validation_fail(self, mock_process_geometry_search, mock_validate_json):
        data = {
            "geometry": '{"crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}, '
            '"coordinates": [257661.0, 52874.0], "type": "Point"}'
        }
        mock_validate_json.return_value = {"errors": ["register validation error"]}
        mock_process_geometry_search.return_value = (
            json.dumps({"errors": ["register validation error"]}),
            400, {"Content-Type": "application/json"}
        )

        response = self.app.post('/records/geometry/intersect', data=json.dumps(data),
                                 headers={"Host": "local-land-charge.my_url.gov.uk",
                                          "Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], "register validation error")

    def test_geometry_search_invalid_sub_domain(self):
        response = self.app.post('/records/geometry/intersect')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode(response.charset))
        self.assertEqual(response_json['errors'][0], 'invalid sub-domain')

post_response = {
    "charge-type": "test",
    "description": "test",
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
    "originating-authority": "test",
    "provision": "test"
}

get_response_many = [
    {
        "charge-type": "test",
        "description": "test",
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
        "originating-authority": "test",
        "provision": "test"
    },
    {
        "charge-type": "test",
        "description": "test",
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
        "originating-authority": "test",
        "provision": "test"
    }
]

get_response_one = {
    "charge-type": "test",
    "description": "test",
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
    "originating-authority": "test",
    "provision": "test"
}

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
