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
    payment_plan = data['payment_plan']
    discount_code = data.get('discount_code')
    
    # Check if the discount code exists
    promotion_code_id = None
    if discount_code:
        try:
            # List promotion codes with the provided code
            promotion_codes = stripe.PromotionCode.list(code=discount_code)
            if promotion_codes.data:
                promotion_code_id = promotion_codes.data[0].id
            else:
                return jsonify({'error': 'Invalid discount code'}), 200
        except stripe.error.InvalidRequestError as e:
            return jsonify({'error': 'Invalid discount code'}), 200

    # Create customer
    customer = stripe.Customer.create(
        email=email,
        payment_method=payment_method,
        invoice_settings={'default_payment_method': payment_method},
    )

    monthly_price_id = 'price_1Q1AbPJd0vBZvn7xQ9kePkjF'
    anual_price_id = 'price_1Q5avwJd0vBZvn7x8MCoiUbI'
    price_id = monthly_price_id if payment_plan == 'monthly' else anual_price_id
    
    # Create subscription
    subscription_data = {
        'customer': customer.id,
        'items': [{'price': price_id}],
        'expand': ['latest_invoice.payment_intent'],
    }
    if promotion_code_id:
        subscription_data['promotion_code'] = promotion_code_id

    subscription = stripe.Subscription.create(**subscription_data)

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
    
    from datetime import datetime, timezone
    
    start = latest_subscription.current_period_start
    end = latest_subscription.current_period_end
    
    # Convert Unix timestamps to UTC datetime
    start_utc = datetime.fromtimestamp(start, tz=timezone.utc)
    end_utc = datetime.fromtimestamp(end, tz=timezone.utc)
    
    # Format the dates to include hours, minutes, seconds, and time zone
    start_date = start_utc.strftime("%m/%d/%Y %H:%M:%S %Z")
    end_date = end_utc.strftime("%m/%d/%Y %H:%M:%S %Z")
    
    return_data = {
        "created": payment_intent.created,
        "amount": payment_intent.amount,
        "status": latest_subscription.status,
        "start_date": start_date,
        "start_timestamp": start,
        "end_date": end_date,
        "end_timestamp": end,
        "cancel_at_period_end": latest_subscription.cancel_at_period_end
    }

    return return_data

# Cancel subscription at end of billing period
@payment_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    data = request.json
    email = data['email']

    try:
        # Retrieve the customer based on the email
        customers = stripe.Customer.list(email=email)
        if not customers.data:
            return jsonify({'error': 'Customer not found'}), 404

        customer_id = customers.data[0].id

        # Retrieve the customer's subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, status='active')
        if not subscriptions.data:
            return jsonify({'error': 'Active subscription not found'}), 404

        subscription_id = subscriptions.data[0].id

        # Update the subscription to cancel at the end of the current period
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return jsonify(subscription)
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400