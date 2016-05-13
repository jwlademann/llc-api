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

valid_keys=["provision","charge-type","description","geometry","originating-authority","authority-charge-id",
            "creation-date","expiration-date","instrument","migrating-authority","old-register-part",
            "place-of-inspection","inspection-reference"
            ]

def update_charge():
    return 'Charge updated'

def create_charge(request):
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        json_in = request.get_json()
        result = register_details[subdomain]['validator'].load(json_in)
        if result.errors:
            return jsonify(result.errors)
        else:
            json_new = remove_excess_fields(json_in)
            requests.post(app.config['LLC_REGISTER_URL'] + "/" +
                          register_details[subdomain]['url_parameter'] + "/items",
                          data=json_new)
        return 'Charge created'
    else:
        return 'invalid sub-domain'

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]

#remove any fields from the incoming json that are not in the spec
def remove_excess_fields(json_in):
    json_new = {}
    for key in json_in:
        if key in valid_keys:
            json_new[key] = json_in[key]

    return json_new