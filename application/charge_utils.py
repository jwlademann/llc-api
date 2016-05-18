from application.schema.validation import (local_land_charge_schema, statutory_provision_schema,
                                           llc_place_of_inspection_schema,
                                           llc_registering_authority_schema)
from application import app
from flask import jsonify, abort
from jsonschema import Draft4Validator
import requests
import copy
import re
import json

register_details = {
    "local-land-charge": {"validator": local_land_charge_schema,
                          "register_name": "local-land-charge"},
    "llc-place-of-inspection": {"validator": llc_place_of_inspection_schema,
                                "register_name": "llc-place-of-inspection"},
    "llc-registering-authority": {"validator": statutory_provision_schema,
                                  "register_name": "llc-registering-authority"},
    "statutory-provision": {"validator": llc_registering_authority_schema,
                            "register_name": "statutory-provision"}
}


def process_get_request(host_url, primary_id=None):
    sub_domain = host_url.split('.')[0]
    if sub_domain in register_details:
        try:
            if primary_id:
                register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                register_details[sub_domain]['register_name'] + "/record/" +
                                primary_id)
            else:
                register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                register_details[sub_domain]['register_name'] + "/records")
            response = requests.get(register_url)

            response.raise_for_status()
            return_value = response.text, response.status_code, {'Content-Type': 'application/json'}
        except requests.HTTPError as e:
            if e.response.text.startswith("<!DOCTYPE HTML"):
                abort(500)
            else:
                return_value = jsonify({"errors": [e.response.text]}), e.response.status_code
        except requests.ConnectionError:
            abort(500)
    else:
        return_value = jsonify({"errors": ['invalid sub-domain']}), 400
    return return_value

def validate_json(request_json, sub_domain, request_method, primary_id=None):
    if sub_domain in register_details:
        # Make a copy of the schema so any changes aren't persisted
        schema = copy.deepcopy(register_details[sub_domain]['validator'])
        if request_method == 'PUT':
            # If it's a PUT request consider it an update. This requires the primary ID value to
            # be specified in the JSON. This must match the vale provided in the URL endpoint so
            # dynamically alter the schema to make the field mandatory and use regex to make sure
            # the values match.
            schema['properties'][register_details[sub_domain]['register_name']] = {
                "type": "string",
                "pattern": "^{}$".format(primary_id)
            }
            schema['required'].append(register_details[sub_domain]['register_name'])
        validator = Draft4Validator(schema)
        errors = []
        for error in validator.iter_errors(request_json):
            # Validate JSON against schema and format error messages
            if error.path:
                pattern = "{0}: {1}"
                errors.append(pattern.format(error.path[0], re.sub('[\^\$]', '', error.message)))
            else:
                pattern = "{0}"
                errors.append(pattern.format(error.message))
                # Remove any fields not defined in the schema from the submitted JSON
        json_new = remove_excess_fields(request_json, schema)
        return_value = {"valid_json": json_new, "errors": errors}
    else:
        return_value = {"valid_json": None, "errors": ['invalid sub-domain']}
    return return_value

def process_update_request(host_url, request_method, request_json, errors=None, primary_id=None):
    sub_domain = host_url.split('.')[0]
    if sub_domain in register_details:
        if errors:
            # If there are errors add array to JSON and return
            result = {"errors": errors}
            return_value = jsonify(result), 400
        else:
            try:
                # Decide which endpoint and request method to use based on incoming request method
                if request_method == 'PUT':
                    register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                    register_details[sub_domain]['register_name'] + "/record/" +
                                    primary_id)
                    response = requests.put(register_url, json=request_json)
                else:
                    register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                    register_details[sub_domain]['register_name'] + "/records")
                    response = requests.post(register_url, json=request_json)
                response.raise_for_status()

                # Construct JSON response containing generated record and the URL to use to retrieve
                # the record in the future.
                json_response = {
                    "href": "{}/record/{}".format(
                        host_url,
                        json.loads(response.text)[register_details[sub_domain]['register_name']]),
                    "record": json.loads(response.text)}
                return_value = jsonify(json_response), response.status_code
            except requests.HTTPError as e:
                if e.response.text.startswith("<!DOCTYPE HTML"):
                    abort(500)
                else:
                    return_value = jsonify({"errors": [e.response.text]}), e.response.status_code
            except requests.ConnectionError:
                abort(500)
    else:
        return_value = jsonify({"errors": ['invalid sub-domain']}), 400
    return return_value

def remove_excess_fields(json_in, schema):
    """remove any fields from the incoming json that are not in the spec"""
    json_new = {}
    for key in json_in:
        if key in schema['properties'].keys():
            json_new[key] = json_in[key]

    return json_new

# def get_subdomain(request):
#     """
#     Obtain the subdomain from the endpoint URL
#     :param request: the Request object
#     :return: The subdomain
#     """
#     return request.headers['Host'].split('.')[0]

# def create_charge(request_json, host_url, request_method, primary_id=None):
#     # Get subdomain from URL to use with register_details dict
#     subdomain = host_url.split('.')[0]
#
#     # Make a copy of the schema so any changes aren't persisted
#     schema = copy.deepcopy(register_details[subdomain]['validator'])
#     if request_method == 'PUT':
#         # If it's a PUT request consider it an update. This requires the primary ID value to
#         # be specified in the JSON. This must match the vale provided in the URL endpoint so
#         # dynamically alter the schema to make the field mandatory and use regex to make sure
#         # the values match.
#         schema['properties'][register_details[subdomain]['register_name']] = {
#             "type": "string",
#             "pattern": "^{}$".format(primary_id)
#         }
#         schema['required'].append(register_details[subdomain]['register_name'])
#     validator = Draft4Validator(schema)
#     errors = []
#     for error in validator.iter_errors(request_json):
#         # Validate JSON against schema and format error messages
#         if error.path:
#             pattern = "{0}: {1}"
#             errors.append(pattern.format(error.path[0], re.sub('[\^\$]', '', error.message)))
#         else:
#             pattern = "{0}"
#             errors.append(pattern.format(error.message))
#
#     if errors:
#         # If there are errors add array to JSON and return
#         result = {"errors": errors}
#         return jsonify(result), 400
#     else:
#         # Remove any fields not defined in the schema from the submitted JSON
#         json_new = remove_excess_fields(request_json, schema)
#         try:
#             # Decide which endpoint and request method to use based on incoming request method
#             if request_method == 'PUT':
#                 register_url = (app.config['LLC_REGISTER_URL'] + "/" +
#                                 register_details[subdomain]['register_name'] + "/record/" + primary_id)
#                 response = requests.put(register_url, json=json_new)
#             else:
#                 register_url = (app.config['LLC_REGISTER_URL'] + "/" +
#                                 register_details[subdomain]['register_name'] + "/records")
#                 response = requests.post(register_url, json=json_new)
#             response.raise_for_status()
#         except requests.HTTPError as e:
#             if e.response.text.startswith("<!DOCTYPE HTML"):
#                 abort(500)
#             else:
#                 return jsonify({"errors": [e.response.text]}), e.response.status_code
#         except requests.ConnectionError:
#             abort(500)
#
#         # Construct JSON response containing generated record and the URL to use to retrieve
#         # the record in the future.
#         json_response = {
#             "href": "{}/record/{}".format(
#                 host_url,
#                 json.loads(response.text)[register_details[subdomain]['register_name']]),
#             "record": json.loads(response.text)}
#         return jsonify(json_response), response.status_code
