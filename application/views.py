from application import app, charges_utils, charge_utils
from flask import request, redirect, url_for
import requests

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"


# curl localhost:5001/v0.1/charges
# curl -X POST localhost:5001/v0.1/charges
@app.route("/<version>/charges", methods=["GET", "POST"])
def charges(version):
    if request.method == 'GET':
        return charges_utils.get_charges(version)
    elif request.method == 'POST':
        return charges_utils.post_charge(version)


# curl localhost:5001/v0.1/charges/12345
# curl -X PUT localhost:5001/v0.1/charges/12345
# curl -X DELETE localhost:5001/v0.1/charges/12345
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
    return get_database_response(request.json)


def get_database_response(test_json):
    r = requests.post('http://llc-register:5002/database', json=test_json)
    return r.text