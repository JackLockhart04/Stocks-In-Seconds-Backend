from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    
    # Load configuration from Config class
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True)

    from app.login import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app