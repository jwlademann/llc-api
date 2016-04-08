from application import app
from flask import request

@app.route("/health")
def check_status():
    return "LLC API running"

@app.route("/<version>/hello", methods=["GET"])
def hello(version):
    return 'Hello ' + version

# curl localhost:5001/v0.1/charges
# curl -X POST localhost:5001/c0.1/charges
@app.route("/<version>/charges", methods=["GET", "POST"])
def charges(version):
    if request.method == 'GET':
        return 'API Version request: ' + version + '. List of charges.'
    elif request.method == 'POST':
        return 'API Version request: ' + version + '. Create new charge.'

# curl localhost:5001/v0.1/charges/12345
# curl -X PUT localhost:5001/c0.1/charges/12345
# curl -X DELETE localhost:5001/c0.1/charges/12345
@app.route("/<version>/charges/<id>", methods=["GET", "PUT", "DELETE"])
def charge(version, id):
    if request.method == 'GET':
        return 'API Version request: ' + version + '. Charge ID: ' + id
    elif request.method == 'PUT':
        return 'API Version request: ' + version + '. Charge ID: ' + id + ' updated.'
    elif request.method == 'DELETE':
        return 'API Version request: ' + version + '. Charge ID: ' + id + ' deleted.'
