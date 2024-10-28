# app.py
from flask import Blueprint, request, jsonify
import stripe

from config import Config

payment_bp = Blueprint('payment', __name__)

# Set your secret key
stripe.api_key = Config.STRIPE_SECRET_KEY 

@payment_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.json
    email = data.get('email')
    payment_method_id = data.get('payment_method_id')
    payment_plan = data.get('payment_plan')
    
    # Define your price IDs based on the payment plan names
    price_ids = {
        'startup_launch': 'price_1QCSgMJd0vBZvn7xbttfZZsa',
        'startup_launch_premium': 'price_1QEzbFJd0vBZvn7xzc6bi1r9'
    }
    price_id = price_ids.get(payment_plan)
    if not price_id:
        return jsonify({'error': 'Invalid payment plan'}), 400

    try:
        # Create customer
        customer = stripe.Customer.create(
            email=email,
            payment_method=payment_method_id,
            invoice_settings={'default_payment_method': payment_method_id},
        )
        
         # Retrieve the price object to get the amount and currency
        price = stripe.Price.retrieve(price_id)

        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=price.unit_amount,  # Use the amount from the price object
            currency=price.currency,   # Use the currency from the price object
            customer=customer.id,
            payment_method=payment_method_id,
            off_session=False,
            confirm=False,
            metadata={
                'email': email,
                'payment_plan': payment_plan,
            },
        )
        
        return jsonify({
            'client_secret': payment_intent.client_secret,
            # 'customer_id': customer.id,
        }), 200
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'message': 'Payment intent created'})