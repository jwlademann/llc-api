from application import app, charge_utils
from flask import request

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"


@app.route("/records", methods=["POST"])
def create_charge():
    return charge_utils.create_charge(request)

@app.route("/record/<primary_id>", methods=["PUT"])
def update_charge(primary_id):
    return charge_utils.create_charge(request, primary_id)
