from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from datetime import datetime
import msal
from app.db.user import User

auth_bp = Blueprint('auth', __name__)

DB_TABLE_NAME = 'stocks-in-seconds-users'

@auth_bp.route('/login', methods=['GET'])
def login():
    msal_app = msal.ConfidentialClientApplication(
        current_app.config["CLIENT_ID"],
        authority=current_app.config["AUTHORITY"],
        client_credential=current_app.config["CLIENT_SECRET"]
    )
    auth_url = msal_app.get_authorization_request_url(
        scopes=current_app.config["SCOPE"],
        redirect_uri=url_for('auth.getAToken', _external=True)
    )

    return redirect(auth_url)

@auth_bp.route('/getAToken', methods=['GET'])
def getAToken():
    msal_app = msal.ConfidentialClientApplication(
        current_app.config["CLIENT_ID"],
        authority=current_app.config["AUTHORITY"],
        client_credential=current_app.config["CLIENT_SECRET"]
    )
    result = msal_app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=current_app.config["SCOPE"],
        redirect_uri=url_for('auth.getAToken', _external=True)
    )

    if "error" in result:
        return jsonify(result), 400
    
    # Set the session
    session["user"] = result.get("id_token_claims")
    
    # Redirect to the user page, response is included
    return redirect('https://stocksinseconds.com/')

@auth_bp.route('/user', methods=['GET'])
def get_user():
    if "user" in session:
        email = session["user"]["preferred_username"]
        session["user"]["email"] = email
        # Retrieve the user from the database
        user = User.get(DB_TABLE_NAME, email)
        if not user:
            # Add the user to the DynamoDB table if not exists
            username = session["user"].get("name", email)
            new_user = User(
                table_name=DB_TABLE_NAME,
                email=email,
                username=username,
                subscription_status=0,  # or any default status you want to set
                last_login=datetime.now().strftime("%m/%d/%Y")  # Get current date in month/day/year format
            )
            # Add to db
            new_user.add()
        else:
            # Update attributes of user (Always last login)
            update_data = {"last_login":datetime.now().strftime("%m/%d/%Y")} # FIXME to my timezone (CDT)
            
            # Update payment info and subscription status if user has made a payment
            from app.payment.routes import get_last_payment
            last_payment_info = get_last_payment(email)

            # If user has made a payment
            if last_payment_info:
                # Update user's subscription status
                last_payment_status = last_payment_info.get("status")
                update_data["subscription_start_date"] = last_payment_info.get("start_date")
                update_data["subscription_end_date"] = last_payment_info.get("end_date")

                # Check subscription status
                if last_payment_status == "active":
                    update_data["subscription_status"] = 1
                    session["user"]["subscription_status"] = 1
                    session["user"]["subscription_start_date"] = last_payment_info.get("start_date")
                    session["user"]["subscription_end_date"] = last_payment_info.get("end_date")
                else:
                    update_data["subscription_status"] = 0
                    session["user"]["subscription_status"] = 0
            else:
                update_data["subscription_status"] = 0
                session["user"]["subscription_status"] = 0
                
            #Update db
            user.update(update_data)
        # Return the user
        return jsonify(session["user"]), 200
    
    # Not logged in
    else:
        return jsonify({'message': 'User not logged in'}), 200


print('Login blueprint registered')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    # Clear the session
    session.clear()

    # Redirect to Microsoft logout endpoint
    logout_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('auth.logged_out', _external=True)}"
    return redirect(logout_url)

@auth_bp.route('/logged_out')
def logged_out():
    # Redirect to the desired URL after logout
    return redirect("https://stocksinseconds.com/")

@auth_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'}), 200