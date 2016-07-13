from application import app, charge_utils
from flask import request
import json


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
    resolve = request.args.get('resolve')
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
        # if sub_domain == "local-land-charge":
        #     try:
        #         if 'geometry' in request.get_json():
        #             geometry = json.loads(request.get_json()['geometry'])
        #             request.get_json()['geometry'] = geometry
        #     except (json.JSONDecodeError, TypeError) as e:
        #         app.logger.warn('Could not decode json: ' + str(e))
        #         pass  # Geometry causing these errors will be caught by validation and returned to the user
        result = charge_utils.validate_json(request.get_json(), sub_domain, request.method)
        resolve = request.args.get('resolve')
        if result['errors']:
            # If there are errors add array to JSON and return
            errors = {"errors": result['errors']}
            return_value = (json.dumps(errors, sort_keys=True), 400,
                            {"Content-Type": "application/json"})
        else:
            return_value = charge_utils.process_update_request(request.headers['Host'],
                                                               request.method,
                                                               request.get_json(),
                                                               resolve=resolve)
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
        resolve = request.args.get('resolve')
        if result['errors']:
            # If there are errors add array to JSON and return
            errors = {"errors": result['errors']}
            return_value = (json.dumps(errors, sort_keys=True), 400,
                            {"Content-Type": "application/json"})
        else:
            return_value = charge_utils.process_update_request(request.headers['Host'],
                                                               request.method,
                                                               request.get_json(),
                                                               primary_id,
                                                               resolve=resolve)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value


@app.route("/records/geometry/<function>", methods=["POST"])
def geometry_search(function):
    sub_domain = request.headers['Host'].split('.')[0]
    if sub_domain == 'local-land-charge':
        result = charge_utils.validate_json(request.get_json(), sub_domain, request.method, search=True)
        if result['errors']:
            # If there are errors add array to JSON and return
            errors = {"errors": result['errors']}
            return_value = (json.dumps(errors, sort_keys=True), 400,
                            {"Content-Type": "application/json"})
        else:
            return_value = charge_utils.process_geometry_search(request.headers['Host'],
                                                                request.get_json(),
                                                                function)
    else:
        return_value = (json.dumps({"errors": ['invalid sub-domain']}), 400,
                        {"Content-Type": "application/json"})

    return return_value
