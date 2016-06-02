from application import app, charge_utils
from flask import request
import json
from json import JSONDecodeError


@app.route("/")
@app.route("/health")
def check_status():
    return request.headers['Host'].split('.')[0] + " API running."


@app.route("/records", methods=["GET"])
def get_charges():
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain in charge_utils.register_details:
        return_value = charge_utils.process_get_request(request.headers['Host'])
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value


@app.route("/record/<primary_id>", methods=["GET"])
def get_charge(primary_id):
    sub_domain = request.headers['Host'].split('.')[0]
    resolve = request.args.get['resolve']
    if sub_domain in charge_utils.register_details:
        return_value = charge_utils.process_get_request(request.headers['Host'], primary_id, resolve)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value


@app.route("/records", methods=["POST"])
def create_charge():
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain in charge_utils.register_details:
        if sub_domain == "local-land-charge":
            try:
                geometry = json.loads(request.get_json()['geometry'])
                request.get_json()['geometry'] = geometry
            except JSONDecodeError as e:
                app.logger.warn('Could not encode json: ' + str(e))
                pass  # let validation handle errors returned to the user
        result = charge_utils.validate_json(request.get_json(), sub_domain, request.method)
        if result['errors']:
            # If there are errors add array to JSON and return
            errors = {"errors": result['errors']}
            return_value = (json.dumps(errors, sort_keys=True), 400,
                            {"Content-Type": "application/json"})
        else:
            return_value = charge_utils.process_update_request(request.headers['Host'],
                                                               request.method,
                                                               request.get_json())
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value


@app.route("/record/<primary_id>", methods=["PUT"])
def update_charge(primary_id):
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain in charge_utils.register_details:
        result = charge_utils.validate_json(request.get_json(), sub_domain, request.method,
                                            primary_id)
        if result['errors']:
            # If there are errors add array to JSON and return
            errors = {"errors": result['errors']}
            return_value = (json.dumps(errors, sort_keys=True), 400,
                            {"Content-Type": "application/json"})
        else:
            return_value = charge_utils.process_update_request(request.headers['Host'],
                                                               request.method,
                                                               request.get_json(),
                                                               primary_id)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value
