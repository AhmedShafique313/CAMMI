import os
from flask import Flask, redirect, jsonify, json, request, render_template
from dotenv import load_dotenv
import stripe

# Load .env file
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

# Configure Stripe API key
stripe.api_key = os.getenv("STRIPE_API_KEY")

app = Flask(__name__)

YOUR_DOMAIN = 'http://127.0.0.1:5000'

# ------------------------
# Routes
# ------------------------

@app.route('/', methods=['GET'])
def index():
    return render_template('checkout.html')


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    prices = stripe.Price.list(
        lookup_keys=[request.form['lookup_key']],
        expand=['data.product']
    )

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': prices.data[0].id,
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + '/cancel',
    )
    return redirect(checkout_session.url, code=303)


@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')


@app.route('/cancel', methods=['GET'])
def cancel():
    return render_template('cancel.html')


@app.route('/create-portal-session', methods=['POST'])
def customer_portal():
    checkout_session_id = request.form.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    if not checkout_session.customer:
        return "Error: No customer found for this session. Did you complete checkout?", 400

    portal_session = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=YOUR_DOMAIN,
    )
    return redirect(portal_session.url, code=303)


@app.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = 'whsec_12345'
    request_data = json.loads(request.data)

    if webhook_secret:
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return str(e), 400
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription updated %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        print('Subscription canceled: %s', event.id)
    elif event_type == 'entitlements.active_entitlement_summary.updated':
        print('Active entitlement summary updated: %s', event.id)

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
