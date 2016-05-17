from application import app, charge_utils
from flask import request

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"

@app.route("/records", methods=["GET", "POST"])
def create_charge():
    if request.method == "GET":
        return charge_utils.get_charge_records(request)
    else:
        return charge_utils.create_charge(request)

@app.route("/record/<primary_id>", methods=["GET", "PUT"])
def update_charge(primary_id):
    if request.method == "GET":
        return charge_utils.get_charge_record(request, primary_id)
    else:
        return charge_utils.create_charge(request, primary_id)
