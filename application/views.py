from flask import render_template
from application import app

@app.route("/")
def check_status():
    return "LLC API running"

@app.route("/data")
def data():
    return render_template("data.html")
