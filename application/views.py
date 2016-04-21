from application import app, charges_utils, charge_utils
from flask import request, redirect, url_for
import json
import requests

@app.route("/health")
def check_status():
    return "LLC API running"


# curl localhost:5001/v0.1/charges
# curl -X POST localhost:5001/c0.1/charges
@app.route("/<version>/charges", methods=["GET", "POST"])
def charges(version):
    if request.method == 'GET':
        return charges_utils.get_charges(version)
    elif request.method == 'POST':
        return charges_utils.post_charge(version)

# curl localhost:5001/v0.1/charges/12345
# curl -X PUT localhost:5001/c0.1/charges/12345
# curl -X DELETE localhost:5001/c0.1/charges/12345
@app.route("/<version>/charges/<id>", methods=["GET", "PUT", "DELETE"])
def charge(version, id):
    if request.method == 'GET':
        return charge_utils.get_charge(version, id)
    elif request.method == 'PUT':
        return charge_utils.put_charge(version, id)
    elif request.method == 'DELETE':
        return charge_utils.delete_charge(version, id)


@app.route("/database", methods=['POST'])
def db_test():
    test_info = {}
    test_info['charge_id'] = request.form['charge_id']
    test_info['description'] = request.form['description']
    test_info['reg_date'] = request.form['reg_date']
    test_info['cre_date'] = request.form['cre_date']
    test_info['exp_date'] = request.form['exp_date']
    test_info['instrument'] = request.form['instrument']
    test_info['mig_auth'] = request.form['mig_auth']
    test_info['charge_type'] = request.form['charge_type']
    test_info['provision'] = request.form['provision']
    test_info['geometry'] = request.form['geometry']
    test_info['old_part'] = request.form['old_part']

    test_json = json.dumps(test_info)

    return get_database_response(test_json)


def get_database_response(test_json):
    r = requests.post('http://llc-register:5002/database', json=test_json)
    return r.text