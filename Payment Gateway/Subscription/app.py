from flask import Flask, render_template, request

app = Flask(__name__)

# ------------------------
# Routes (Frontend only)
# ------------------------

@app.route("/", methods=["GET"])
def index():
    # This will show your checkout.html page
    return render_template("checkout.html")

@app.route("/success", methods=["GET"])
def success():
    # Stripe redirects here after successful payment
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)

@app.route("/cancel", methods=["GET"])
def cancel():
    # Stripe redirects here if payment is cancelled
    return render_template("cancel.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)