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
    tb_lines = traceback.format_exception(error.__class__, error, error.__traceback__)
    tb_text = ''.join(tb_lines)
    app.logger.error(tb_text)
    return (json.dumps({"errors": [error]}), 500, {"Content-Type": "application/json"})


@app.route("/records", methods=["GET"])
def get_records():
    sub_domain = request.headers['Host'].split('.')[0]
    resolve = request.args.get('resolve')
    if sub_domain not in register_utils.REGISTER_INFO:
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, None)
    if response.status_code != 200:
        return_value = json.dumps({"errors": [response.text]})
    else:
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/record/<primary_id>", methods=["GET"])
def get_record(primary_id):
    sub_domain = request.headers['Host'].split('.')[0]
    resolve = request.args.get('resolve')
    if sub_domain not in register_utils.REGISTER_INFO:
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, None)
    if response.status_code != 200:
        return_value = json.dumps({"errors": [response.text]})
    else:
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/records", methods=["POST"])
def create_record():
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    result = register_utils.validate_json(sub_domain, '/records', request.method, json_payload)
    if len(result['errors']) > 0:
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    result = register_utils.additional_validation(sub_domain, request.path, '/records', request.method, json_payload)
    if len(result['errors']) > 0:
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 201:
        return_value = json.dumps({"errors": [response.text]})
    else:
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/record/<primary_id>", methods=["PUT"])
def update_record(primary_id):
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    result = register_utils.validate_json(sub_domain, '/record/<primary_id>', request.method, json_payload)
    if len(result['errors']) > 0:
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    result = register_utils.additional_validation(sub_domain, request.path, '/record/<primary_id>', request.method, json_payload)
    if len(result['errors']) > 0:
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 200:
        return_value = json.dumps({"errors": [response.text]})
    else:
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})


@app.route("/records/geometry/<function>", methods=["POST"])
def geometry_search(function):
    sub_domain = request.headers['Host'].split('.')[0]
    json_payload = request.get_json()
    if sub_domain not in register_utils.REGISTER_INFO or not register_utils.REGISTER_INFO[sub_domain]['geometry-search']:
        return (json.dumps({"errors": ['invalid sub-domain']}), 400, {"Content-Type": "application/json"})
    result = register_utils.validate_json(sub_domain, '/records/geometry/<function>', request.method, json_payload)
    if len(result['errors']) > 0:
        return (json.dumps(result), 400, {"Content-Type": "application/json"})
    resolve = request.args.get('resolve')
    response = register_utils.register_request(sub_domain, request.path, ["resolve={}".format(resolve)], request.method, json_payload)
    if response.status_code != 200:
        return_value = json.dumps({"errors": [response.text]})
    else:
        return_value = json.dumps(response.json(), sort_keys=True)
    return (return_value, response.status_code, {"Content-Type": "application/json"})
