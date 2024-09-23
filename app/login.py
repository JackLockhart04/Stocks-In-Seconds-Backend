from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
import msal
auth_bp = Blueprint('auth', __name__)

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
        return jsonify(session["user"])
    return jsonify({'message': 'User not logged in'}), 401


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