from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app, make_response
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
    
    # Include additional data in the redirect URL as query parameters
    redirect_url = 'https://stocksinseconds.com/account'

    # Redirect to the external URL with additional data
    return redirect(redirect_url)

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
                last_login=datetime.now().strftime("%m/%d/%Y")  # Get current date in month/day/year format
            )
            # Add to db
            new_user.add()
        else:
            # Update attributes of user (Always last login)
            update_data = {"last_login":datetime.now().strftime("%m/%d/%Y")}
                
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
