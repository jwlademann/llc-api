from application import app

@app.route("/health")
def check_status():
    return "LLC API running"
