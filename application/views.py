from application import app, charge_utils
from flask import request

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"


@app.route("/records", methods=["PUT", "POST"])
def charges():
    return charge_utils.create_charge(request)
