from application import app
from flask import abort
from jsonschema.validators import validator_for
from datetime import datetime
import requests
import copy
import re
import os
import json

register_details = {
    "local-land-charge": {"filename": "local-land-charge-swagger.json",
                          "definition_name": "Local-Land-Charge",
                          "register_name": "local-land-charge"},
    "llc-place-of-inspection": {"filename": "further-information-location-swagger.json",
                                "definition_name": "Place-of-Inspection",
                                "register_name": "llc-place-of-inspection"},
    "llc-registering-authority": {"filename": "registering-authority-swagger.json",
                                  "definition_name": "Registering-Authority",
                                  "register_name": "llc-registering-authority"},
    "statutory-provision": {"filename": "statutory-provision-swagger.json",
                            "definition_name": "Statutory-Provision",
                            "register_name": "statutory-provision"}
}


def _format_error_messages(error, sub_domain):
    error_message = error.message

    # Format error message for empty string regex to be more user friendly
    if " does not match '\\\\S+'" in error.message:
        error_message = "must not be blank"

    # Format error message for Curie regex to be more user friendly
    if " does not match '\\\\S+:\\\\d+'" in error.message:
        error_message = "must be specified as a Curie e.g. statutory-provision:1234"

    # For primary key validation remove start/end of line regex characters from error message for clarity
    if register_details[sub_domain]['register_name'] in error.path:
        error_message = re.sub('\^(.*)\$', '\\1', error.message)

    # Get element names of erroring fields if required
    path = []
    for element in error.path:
        if isinstance(element, str):
            path.append(element)

    element_id = ".".join(path)
    if element_id:
        element_id = "'{}'".format(element_id)

    return " ".join(list(filter(None, [element_id, error_message])))


def validate_helper(json_to_validate, sub_domain, request_method, primary_id):
    errors = []
    validator = _create_llc_validator(sub_domain, request_method, primary_id)
    error_list = sorted(validator.iter_errors(json_to_validate),
                        key=str, reverse=True)

    for count, error in enumerate(error_list, start=1):
        errors.append("Problem %s: %s" % (count, _format_error_messages(error, sub_domain)))

    validate_date(errors, json_to_validate)

    return errors


def validate_date(errors, json_to_validate):

    dates = ["creation-date", "expiration-date"]
    for date in dates:
        try:
            if date in json_to_validate:
                datetime.strptime(json_to_validate[date], "%d/%m/%Y")
        except ValueError:
            error_message = "'%s' " % date + "is an invalid date"
            errors.append("Problem %s: %s" % (len(errors) + 1, error_message))


def get_swagger_file(sub_domain):
    return load_json_file(os.getcwd() + "/application/schema/%s" % register_details[sub_domain]['filename'])


def load_json_schema(sub_domain):
    swagger = get_swagger_file(sub_domain)

    definitions = swagger["definitions"]

    record_definition = definitions[register_details[sub_domain]['definition_name']]

    record = {
        "definitions": definitions,
        "properties": record_definition["properties"],
        "required": record_definition["required"],
        "type": "object",
        "additionalProperties": False
    }

    return record


def _create_llc_validator(sub_domain, request_method, primary_id):
    schema = copy.deepcopy(load_json_schema(sub_domain))

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
    elif request_method == 'POST':
        # If POST request remove 'local-land-charge' from properties as it shouldn't be provided
        schema['properties'].pop(register_details[sub_domain]['register_name'])

    validator = validator_for(schema)
    validator.check_schema(schema)
    return validator(schema)


def load_json_file(file_path):
    with open(file_path, 'rt') as file:
        json_data = json.load(file)

    return json_data


def process_get_request(host_url, primary_id=None, resolve='0'):

    sub_domain = host_url.split('.')[0]
    if sub_domain in register_details:
        try:
            if primary_id:
                register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                register_details[sub_domain]['register_name'] + "/record/" +
                                primary_id)
                if resolve == '1':
                    register_url += '?resolve=1'
            else:
                register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                register_details[sub_domain]['register_name'] + "/records")
            response = requests.get(register_url)

            response.raise_for_status()
            return_value = (response.text, response.status_code,
                            {'Content-Type': 'application/json'})
        except requests.HTTPError as e:
            if e.response.text.startswith("<!DOCTYPE HTML"):
                abort(500)
            else:
                return_value = (json.dumps({"errors": [e.response.text]}), e.response.status_code,
                                {"Content-Type": "application/json"})
        except requests.ConnectionError:
            abort(500)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})
    return return_value


def validate_json(request_json, sub_domain, request_method, primary_id=None):
    if sub_domain in register_details:
        errors = validate_helper(request_json, sub_domain, request_method, primary_id)
        return_value = {"errors": errors}
    else:
        return_value = {"errors": ['invalid sub-domain']}
    return return_value


def process_update_request(host_url, request_method, request_json, primary_id=None):
    sub_domain = host_url.split('.')[0]
    if sub_domain in register_details:
        try:
            # Decide which endpoint and request method to use based on incoming request method
            if request_method == 'PUT':
                register_url = (app.config['LLC_REGISTER_URL'] + "/" +
                                register_details[sub_domain]['register_name'] + "/record/" +
                                str(primary_id))
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
            return_value = (json.dumps(json_response, sort_keys=True), response.status_code,
                            {"Content-Type": "application/json"})
        except requests.HTTPError as e:
            if e.response.text.startswith("<!DOCTYPE HTML"):
                abort(500)
            else:
                return_value = (json.dumps({"errors": [e.response.text]}), e.response.status_code,
                                {"Content-Type": "application/json"})
        except requests.ConnectionError:
            abort(500)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})
    return return_value
