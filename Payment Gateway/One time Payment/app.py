import os
from flask import Flask, redirect, request, render_template
import stripe
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

# This is your test secret API key
stripe.api_key = os.getenv("STRIPE_API_KEY")

app = Flask(__name__)

YOUR_DOMAIN = 'http://127.0.0.1:5000'

# ---------- ROUTES ----------

@app.route('/')
def index():
    # Show the checkout page (main page)
    return render_template('checkout.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1SCe9w1LHsiGbvuaBwykahw6', 
                    'quantity': 1,
                },
            ],
            mode='payment',   # change to 'subscription' later for SaaS plans
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)
