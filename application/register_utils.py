import flask
import requests

from application import app, charge_validators, register_validators
import jsonschema
import ramlfications


REGISTER_INFO = {
    "local-land-charge": {
        "raml": ramlfications.parse(app.static_folder + '/schema/local-land-charge.raml'),
        "additional-validation": [charge_validators.validate_s8_compensation_charge, charge_validators.validate_s8_compensation_charge,
                                  charge_validators.validate_instrument_provisions, register_validators.validate_primary_id],
        "primary-id": "local-land-charge",
        "geometry-search": True
    },
    "further-information-location": {
        "raml": ramlfications.parse(app.static_folder + '/schema/further-information-location.raml'),
        "additional-validation": [register_validators.validate_primary_id],
        "primary-id": "further-information-location",
        "geometry-search": False
    },
    "llc-registering-authority": {
        "raml": ramlfications.parse(app.static_folder + '/schema/llc-registering-authority.raml'),
        "additional-validation": [register_validators.validate_primary_id],
        "primary-id": "llc-registering-authority",
        "geometry-search": False
    },
    "statutory-provision": {
        "raml": ramlfications.parse(app.static_folder + '/schema/statutory-provision.raml'),
        "additional-validation": [register_validators.validate_primary_id],
        "primary-id": "statutory-provision",
        "geometry-search": False
    }
}
# Resolver to get json schemas from relative paths
RELATIVE_RESOLVER = jsonschema.RefResolver('file://' + app.static_folder + '/schema/', None)


def validate_json(sub_domain, end_point_pattern, method, json_payload):
    """Validation the given json for the given end point and method for the given register sub domain
    """
    if sub_domain not in REGISTER_INFO:
        return {"errors": ['invalid sub-domain']}
    # Get RAML resource
    raml = REGISTER_INFO[sub_domain]["raml"]
    raml_end_point = end_point_pattern.replace('<', '{').replace('>', '}')
    raml_resource = None
    for resource in raml.resources:
        if resource.path == raml_end_point and resource.method.lower() == method.lower():
            raml_resource = resource
            break
    if not raml_resource:
        return {"errors": ['cannot find RAML resource definition']}
    raml_schema = None
    # Get schema name from RAML resource
    if raml_resource.body:
        for body in raml_resource.body:
            if body.mime_type == "application/json":
                schema_name = body.schema
                for schema in raml.schemas:
                    if schema_name in schema:
                        raml_schema = schema[schema_name]
                        break
                break
    if not raml_schema:
        return {"errors": ['cannot find schema in RAML resource definition']}
    # Load schema and validate against it
    try:
        validator = jsonschema.Draft4Validator(raml_schema, resolver=RELATIVE_RESOLVER)
    except jsonschema.SchemaError:
        return {"errors": ['invalid json schema']}
    errors = sorted(validator.iter_errors(json_payload), key=lambda e: e.path)
    error_return = []
    for error in errors:
        error_return.append("{}, {}".format(str(list(error.schema_path)), error.message))
        for suberror in sorted(error.context, key=lambda e: e.schema_path):
            error_return.append("{}, {}".format(str(list(suberror.schema_path)), suberror.message))
    return {"errors": error_return}


def additional_validation(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Perform additional validation based on given parameters
    """
    if sub_domain not in REGISTER_INFO:
        return {"errors": ['invalid sub-domain']}
    error_return = []
    for validator in REGISTER_INFO[sub_domain]["additional-validation"]:
        result = validator(sub_domain, end_point, end_point_pattern, method, json_payload)
        error_return = error_return + result['errors']
    return {"errors": error_return}


def retrieve_curie(curie):
    """Lookup the given curie and return record if found/valid, else return None
    """
    register, primary_id = curie.split(':')
    if register not in REGISTER_INFO:
        raise Exception("Invalid register name '{}'".format(register))
    response = register_request(register, "/record/" + primary_id, [], 'get', None)
    if response.status_code == 404:
        return None
    if response.status_code == 200:
        return response.json()
    response.raise_for_status()


def register_request(sub_domain, end_point, parameters, method, json_payload):
    """Send request to register backend
    """
    try:
        response = getattr(requests, method.lower())("{}/{}{}?{}".format(app.config['LLC_REGISTER_URL'], sub_domain, end_point, '&'.join(parameters)),
                                                     json=json_payload)
    except requests.HTTPError as e:
        if e.response.text.startswith("<!DOCTYPE HTML"):
            flask.abort(500)
        else:
            return e.response
    return response
