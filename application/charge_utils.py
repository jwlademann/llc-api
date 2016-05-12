from application.validators import ChargeSchema, FurtherInfoSchema, AuthoritySchema, ProvisionSchema
from application import app
import requests

register_details = {
    "local-land-charge": {"validator": ChargeSchema, "url_parameter": "local-land-charge"},
    "further-information": {"validator": FurtherInfoSchema, "url_parameter": "further-information"},
    "originating-authority": {"validator": AuthoritySchema, "url_parameter": "originating-authority"},
    "statutory-provision": {"validator": ProvisionSchema, "url_parameter": "statutory-provision"}
}

def update_charge():
    return 'Charge updated'

def create_charge(request):
    subdomain = get_subdomain(request)
    result = register_details[subdomain]['validator'].loads(request.get_json())
    if result.errors:
        return result.errors
    else:
        requests.post(app.config['LLC_REGISTER_URL'] + "/" +
                      register_details[subdomain]['url_parameter'] + "/items",
                      data=request.get_json())

def get_subdomain(request):
    return request.headers['Host'].split('.')[0]
