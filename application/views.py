from application import app, charge_utils
from flask import request, jsonify

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"

@app.route("/records", methods=["GET", "POST"])
def create_charge():
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain in charge_utils.register_details:
        if request.method == "GET":
            return_value = charge_utils.process_get_request(request.headers['Host'])
        else:
            result = charge_utils.validate_json(request.get_json(), sub_domain, request.method)
            return_value = charge_utils.process_update_request(request.headers['Host'], request.method,
                                                       result['valid_json'], result['errors'])
    else:
        return_value = jsonify({"errors": ['invalid sub-domain']}), 400

    return return_value

@app.route("/record/<primary_id>", methods=["GET", "PUT"])
def update_charge(primary_id):
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain in charge_utils.register_details:
        if request.method == "GET":
            return_value = charge_utils.process_get_request(request.headers['Host'], primary_id)
        else:
            result = charge_utils.validate_json(request.get_json(), sub_domain, request.method,
                                                primary_id)
            return_value = charge_utils.process_update_request(request.headers['Host'], request.method,
                                                       result['valid_json'], result['errors'],
                                                       primary_id)
    else:
        return_value = jsonify({"errors": ['invalid sub-domain']}), 400

    return return_value
