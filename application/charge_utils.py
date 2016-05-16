from application.schema.validation import (local_land_charge_schema, statutory_provision_schema,
                                           llc_place_of_inspection_schema,
                                           llc_registering_authority_schema)
from application import app
from flask import jsonify
from jsonschema import Draft4Validator
import requests
import copy

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


def create_charge(request):
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        json_in = request.get_json()
        schema = copy.deepcopy(register_details[subdomain]['validator'])
        if request.method == 'PUT':
            schema['properties'][register_details[subdomain]['url_parameter']] = {"type": "string"}
            schema['required'].append(register_details[subdomain]['url_parameter'])
        validator = Draft4Validator(schema)
        errors = []
        for error in validator.iter_errors(json_in):
            errors.append(error.message)

        if errors:
            result = {"errors": errors}
            return jsonify(result), 400
        else:
            json_new = remove_excess_fields(json_in, subdomain)
            register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                            register_details[subdomain]['url_parameter'] + "/items")
            # return register_url
            if request.method == "POST":
                response = requests.post(register_url, json=json_new)
            else:
                response = requests.put(register_url, json=json_new)
            response.raise_for_status()

            return 'Charge created', 201
    else:
        return 'invalid sub-domain', 400

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]

def remove_excess_fields(json_in, subdomain):
    """remove any fields from the incoming json that are not in the spec"""
    json_new = {}
    for key in json_in:
        if key in register_details[subdomain]['validator']['properties'].keys():
            json_new[key] = json_in[key]

    return json_new