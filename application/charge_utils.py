from application.validators import ChargeSchema, PlaceOfInspectionSchema, AuthoritySchema, ProvisionSchema
from application import app
import requests
from flask import jsonify

register_details = {
    "local-land-charge": {"validator": ChargeSchema(), "url_parameter": "local-land-charge"},
    "llc-place-of-inspection": {"validator": PlaceOfInspectionSchema(), "url_parameter": "llc-place-of-inspection"},
    "llc-registering-authority": {"validator": AuthoritySchema(), "url_parameter": "llc-registering-authority"},
    "statutory-provision": {"validator": ProvisionSchema(), "url_parameter": "statutory-provision"}
}

valid_keys={
    "local-land-charge": ["provision","charge-type","description","geometry","originating-authority","authority-charge-id",
            "creation-date","expiration-date","instrument","migrating-authority","old-register-part",
            "place-of-inspection","inspection-reference"
            ],
    "llc-place-of-inspection": ["location"],
    "llc-registering-authority": ["name"],
    "statutory-provision": ["description"]
}

def update_charge():
    return 'Charge updated'

def create_charge(request):
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        json_in = request.get_json()
        errors = register_details[subdomain]['validator'].validate(json_in)
        if errors:
            return jsonify(errors)
        else:
            json_new = remove_excess_fields(json_in, subdomain)
            requests.post(app.config['LLC_REGISTER_URL'] + "/" +
                          register_details[subdomain]['url_parameter'] + "/items",
                          data=json_new)
        return 'Charge created'
    else:
        return 'invalid sub-domain'

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]

def remove_excess_fields(json_in, subdomain):
    """remove any fields from the incoming json that are not in the spec"""
    json_new = {}
    for key in json_in:
        if key in valid_keys[subdomain]:
            json_new[key] = json_in[key]

    return json_new