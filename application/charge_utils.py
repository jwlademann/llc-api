from application.schema.validation import (local_land_charge_schema, statutory_provision_schema,
                                           llc_place_of_inspection_schema,
                                           llc_registering_authority_schema)
from application import app
from flask import jsonify, abort
from jsonschema import Draft4Validator
import requests
import copy
import re

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


def create_charge(request, primary_id=None):
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        schema = copy.deepcopy(register_details[subdomain]['validator'])
        if request.method == 'PUT':
            schema['properties'][register_details[subdomain]['url_parameter']] = {"type": "string",
                                                                                  "pattern": "^{}$".format(primary_id)}
            schema['required'].append(register_details[subdomain]['url_parameter'])
        validator = Draft4Validator(schema)
        errors = []
        for error in validator.iter_errors(request.get_json()):
            if error.path:
                pattern = "{1}: {0}"
                errors.append(pattern.format(re.sub('[\^\$]', '', error.message), error.path[0]))
            else:
                pattern = "{0}"
                errors.append(pattern.format(error.message))

        if errors:
            result = {"errors": errors}
            return jsonify(result), 400
        else:
            json_new = remove_excess_fields(request.get_json(), schema)
            try:
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
                return jsonify({"errors": [e.response.text]}), e.response.status_code
            except requests.ConnectionError:
                abort(500)

            return response.text, response.status_code
    else:
        return 'invalid sub-domain', 400

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]

def remove_excess_fields(json_in, schema):
    """remove any fields from the incoming json that are not in the spec"""
    json_new = {}
    for key in json_in:
        if key in schema['properties'].keys():
            json_new[key] = json_in[key]

    return json_new
