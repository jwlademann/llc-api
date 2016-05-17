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
                          "url_parameter": "local-land-charge"},
    "llc-place-of-inspection": {"validator": llc_place_of_inspection_schema,
                                "url_parameter": "llc-place-of-inspection"},
    "llc-registering-authority": {"validator": statutory_provision_schema,
                                  "url_parameter": "llc-registering-authority"},
    "statutory-provision": {"validator": llc_registering_authority_schema,
                            "url_parameter": "statutory-provision"}
}


def get_charge_records(request):
    """
    Retrieve all records.

    :param request: The HTTP request object
    :return: JSON containing all records
    """
    subdomain = get_subdomain(request)
    try:
        register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                        register_details[subdomain]['url_parameter'] + "/records")
        response = requests.get(register_url)

        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.text.startswith("<!DOCTYPE HTML"):
            abort(500)
        else:
            return jsonify({"errors": [e.response.text]}), e.response.status_code
    except requests.ConnectionError:
        abort(500)

    return response.text, response.status_code, {'Content-Type': 'application/json'}

def get_charge_record(request, primary_id):
    """
    Retrieve a specific record

    :param request: The HTTP request object
    :param primary_id: The ID of the record being retrieved
    :return: JSON containing the record
    """
    subdomain = get_subdomain(request)
    try:
        register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                        register_details[subdomain]['url_parameter'] + "/record/" + primary_id)
        response = requests.get(register_url)

        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.text.startswith("<!DOCTYPE HTML"):
            abort(500)
        else:
            return jsonify({"errors": [e.response.text]}), e.response.status_code
    except requests.ConnectionError:
        abort(500)

    return response.text, response.status_code, {'Content-Type': 'application/json'}

def create_charge(request, primary_id=None):
    """
    Submit a new or updated record entry

    :param request: The HTTP request object
    :param primary_id: The ID of the record being added in the case of an update
    :return: JSON containing the record added and the URL to use to retrieve it
    """
    # Get subdomain from URL to use with register_details dict
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        # Make a copy of the schema so any changes aren't persisted
        schema = copy.deepcopy(register_details[subdomain]['validator'])
        if request.method == 'PUT':
            # If it's a PUT request consider it an update. This requires the primary ID value to
            # be specified in the JSON. This must match the vale provided in the URL endpoint so
            # dynamically alter the schema to make the field mandatory and use regex to make sure
            # the values match.
            schema['properties'][register_details[subdomain]['url_parameter']] = {
                "type": "string",
                "pattern": "^{}$".format(primary_id)
            }
            schema['required'].append(register_details[subdomain]['url_parameter'])
        validator = Draft4Validator(schema)
        errors = []
        for error in validator.iter_errors(request.get_json()):
            # Validate JSON against schema and format error messages
            if error.path:
                pattern = "{0}: {1}"
                errors.append(pattern.format(error.path[0], re.sub('[\^\$]', '', error.message)))
            else:
                pattern = "{0}"
                errors.append(pattern.format(error.message))

        if errors:
            # If there are errors add array to JSON and return
            result = {"errors": errors}
            return jsonify(result), 400
        else:
            # Remove any fields not defined in the schema from the submitted JSON
            json_new = remove_excess_fields(request.get_json(), schema)
            try:
                # Decide which endpoint and request method to use based on incoming request method
                if request.method == 'PUT':
                    register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                    register_details[subdomain]['url_parameter'] + "/record/" + primary_id)
                    response = requests.put(register_url, json=json_new)
                else:
                    register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                    register_details[subdomain]['url_parameter'] + "/records")
                    response = requests.post(register_url, json=json_new)
                response.raise_for_status()
            except requests.HTTPError as e:
                if e.response.text.startswith("<!DOCTYPE HTML"):
                    abort(500)
                else:
                    return jsonify({"errors": [e.response.text]}), e.response.status_code
            except requests.ConnectionError:
                abort(500)

            # Construct JSON response containing generated record and the URL to use to retrieve
            # the record in the future.
            json_response = {
                "href": "{}/record/{}".format(
                    request.headers['Host'],
                    json.loads(response.text)[register_details[subdomain]['url_parameter']]),
                "record": json.loads(response.text)}
            return jsonify(json_response), response.status_code
    else:
        return 'invalid sub-domain', 400

def get_subdomain(request):
    """
    Obtain the subdomain from the endpoint URL
    :param request: the Request object
    :return: The subdomain
    """
    return request.headers['Host'].split('.')[0]

def remove_excess_fields(json_in, schema):
    """remove any fields from the incoming json that are not in the spec"""
    json_new = {}
    for key in json_in:
        if key in schema['properties'].keys():
            json_new[key] = json_in[key]

    return json_new
