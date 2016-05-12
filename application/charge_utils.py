from application.validators import ChargeSchema, FurtherInfoSchema, AuthoritySchema, ProvisionSchema
from application import app
import requests
from flask import jsonify

register_details = {
    "local-land-charge": {"validator": ChargeSchema(), "url_parameter": "local-land-charge"},
    "lc-place-of-inspection": {"validator": FurtherInfoSchema(), "url_parameter": "lc-place-of-inspection"},
    "llc-registering-authority": {"validator": AuthoritySchema(), "url_parameter": "llc-registering-authority"},
    "statutory-provision": {"validator": ProvisionSchema(), "url_parameter": "statutory-provision"}
}

def update_charge():
    return 'Charge updated'

def create_charge(request):
    subdomain = get_subdomain(request)
    if subdomain in register_details:
        result = register_details[subdomain]['validator'].load(request.get_json())
        if result.errors:
            return jsonify(result.errors)
        else:
            requests.post(app.config['LLC_REGISTER_URL'] + "/" +
                          register_details[subdomain]['url_parameter'] + "/items",
                          data=request.get_json())
        return 'Charge created'
    else:
        return 'invalid sub-domain'

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]
