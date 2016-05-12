from application import app, charges_utils, charge_utils
from flask import request, redirect, url_for
import requests

@app.route("/")
@app.route("/health")
def check_status():
    return "LLC API running"


@app.route("/items", methods=["PUT", "POST"])
def charges():
    if request.method == 'PUT':
        return charge_utils.update_charge()
    elif request.method == 'POST':
        return charge_utils.create_charge()

