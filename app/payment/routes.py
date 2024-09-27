# app.py
from flask import Blueprint, request, jsonify
import stripe

payment_bp = Blueprint('payment', __name__)

# Set your secret key
stripe.api_key = 'sk_test_51PwVi0Jd0vBZvn7xsDvS4R08zhutEozFQF9Ghk4xZf8tB2C4CbQXWcPdxrLfnVxj3zX8U7hiWpt4etnvimKHi03M00X079QEZ4'

@payment_bp.route('/create-subscription', methods=['POST'])
def create_subscription():
    data = request.json
    email = data['email']
    payment_method = data['payment_method']

    # Create customer
    customer = stripe.Customer.create(
        email=email,
        payment_method=payment_method,
        invoice_settings={'default_payment_method': payment_method},
    )

    price_id = 'price_1Q1AbPJd0vBZvn7xQ9kePkjF'
    
    # Create subscription
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{'price': price_id}],
        expand=['latest_invoice.payment_intent'],
    )

    return jsonify(subscription)

# Function to get the last payment of a user with a certain email
@payment_bp.route('/get-last-payment', methods=['POST'])
def get_payment():
    data = request.json
    email = data['email']

    payment_intent = get_last_payment(email)

    if not payment_intent:
        return jsonify({'error': 'No payment found for this user'})

    return jsonify(payment_intent)

def get_last_payment(email):
    # Search for the customer by email
    customers = stripe.Customer.list(email=email).data
    if not customers:
        return None

    customer = customers[0]

    # Retrieve the customer's subscriptions
    subscriptions = stripe.Subscription.list(customer=customer.id).data
    if not subscriptions:
        return None
    
    # Filter out canceled subscriptions and get the latest active subscription
    active_subscriptions = [sub for sub in subscriptions if sub.status != 'canceled']
    if not active_subscriptions:
        return None

    # Get the latest subscription
    latest_subscription = subscriptions[0]

    # Get the latest invoice
    latest_invoice = stripe.Invoice.retrieve(latest_subscription.latest_invoice)

    # Get the payment intent
    payment_intent = stripe.PaymentIntent.retrieve(latest_invoice.payment_intent)

    return payment_intent