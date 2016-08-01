import json
import traceback
from flask import request

from application import app, register_utils


@app.route("/")
@app.route("/health")
def check_status():
    return request.headers['Host'].split('.')[0] + " API running."


@app.errorhandler(Exception)
def internal_exception_handler(error):
    """Catch all for logging unexcepted errors
    """
    tb_lines = traceback.format_exception(error.__class__, error, error.__traceback__)
    tb_text = ''.join(tb_lines)
    app.logger.error(tb_text)
    return (json.dumps({"errors": [str(error)]}), 500, {"Content-Type": "application/json"})


@app.route("/records", methods=["GET"])
def get_records():
    """Retrieve all records for register (indicated by sub-domain)
    """
    sub_domain = request.headers['Host'].split('.')[0]
    resolve = request.args.get('resolve')
    if sub_domain not in register_utils.REGISTER_INFO:
        app.logger.warn("Invalid sub-domain '{}' used for records retrieval".format(sub_domain))
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, None)
    if response.status_code != 200:
        app.logger.error("Failed to retrieve records for sub-domain '{}' response was '{}'".format(sub_domain, response.text))
        return_value = json.dumps({"errors": [response.text]})
    else:
        app.logger.info("Retrieved records for sub-domain '{}'".format(sub_domain))
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/record/<primary_id>", methods=["GET"])
def get_record(primary_id):
    """Get record for the given identifier for register (indicated by sub-domain)
    """
    sub_domain = request.headers['Host'].split('.')[0]
    resolve = request.args.get('resolve')
    if sub_domain not in register_utils.REGISTER_INFO:
        app.logger.warn("Invalid sub-domain '{}' used for record retrieval".format(sub_domain))
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, None)
    if response.status_code != 200:
        app.logger.warn("Failed to retrieve record '{}' for sub-domain '{}' response was '{}'".format(primary_id, sub_domain, response.text))
        return_value = json.dumps({"errors": [response.text]})
    else:
        app.logger.info("Retrieved record '{}' for sub-domain '{}'".format(primary_id, sub_domain))
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/records", methods=["POST"])
def create_record():
    """Create records using given JSON for register (indicated by sub-domain)
    """
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    result = register_utils.validate_json(sub_domain, '/records', request.method, json_payload)
    if len(result['errors']) > 0:
        app.logger.warn("Error validating create json for sub-domain '{}' error(s) were '{}'".format(sub_domain, str(result['errors'])))
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    result = register_utils.additional_validation(sub_domain, request.path, '/records', request.method, json_payload)
    if len(result['errors']) > 0:
        app.logger.warn("Error in additional validation of create json for sub-domain '{}' error(s) were '{}'".format(sub_domain, str(result['errors'])))
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 201:
        app.logger.warn("Failure creating record for sub-domain '{}' response was '{}'".format(sub_domain, response.text))
        return_value = json.dumps({"errors": [response.text]})
        headers = {"Content-Type": "application/json"}
    else:
        app.logger.info("Created record for sub-domain '{}'".format(sub_domain))
        record = response.json()
        return_value = json.dumps(record, sort_keys=True)
        headers = {"Content-Type": "application/json",
                   "Location": "{}record/{}".format(request.url_root, record[register_utils.REGISTER_INFO[sub_domain]['primary-id']])}
    return (return_value, response.status_code, headers)


@app.route("/record/<primary_id>", methods=["PUT"])
def update_record(primary_id):
    """Update given record using given JSON for register (indicated by sub-domain)
    """
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    result = register_utils.validate_json(sub_domain, '/record/<primary_id>', request.method, json_payload)
    if len(result['errors']) > 0:
        app.logger.warn("Error validating update json for sub-domain '{}' error(s) were '{}'".format(sub_domain, str(result['errors'])))
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    result = register_utils.additional_validation(sub_domain, request.path, '/record/<primary_id>', request.method, json_payload)
    if len(result['errors']) > 0:
        app.logger.warn("Error in additional validation of update json for sub-domain '{}' error(s) were '{}'".format(sub_domain, str(result['errors'])))
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 200:
        app.logger.warn("Failure updating record '{}' for sub-domain '{}' response was '{}'".format(primary_id, sub_domain, response.text))
        return_value = json.dumps({"errors": [response.text]})
    else:
        app.logger.info("Updated record '{}' for sub-domain '{}'".format(primary_id, sub_domain))
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/records/geometry/<function>", methods=["POST"])
def geometry_search(function):
    """Search for record using given geometry according to given function for register (indicated by sub-domain)
    """
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    if sub_domain not in register_utils.REGISTER_INFO or not register_utils.REGISTER_INFO[sub_domain]['geometry-search']:
        app.logger.warn("Invalid sub-domain '{}' used for geometry search".format(sub_domain))
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    result = register_utils.validate_json(sub_domain, '/records/geometry/<function>', request.method, json_payload)
    if len(result['errors']) > 0:
        app.logger.warn("Error validating geometry search json for sub-domain '{}' error(s) were '{}'".format(sub_domain, str(result['errors'])))
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 200:
        app.logger.warn("Failure geometry searching for sub-domain '{}' response was '{}'".format(sub_domain, response.text))
        return_value = json.dumps({"errors": [response.text]})
    else:
        app.logger.info("Geometry search completed for sub-domain '{}'".format(sub_domain))
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})
