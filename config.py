import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    AUTHORITY = os.getenv('AUTHORITY')
    REDIRECT_PATH = "/auth/getAToken"
    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"

    # Cookies
    SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-site cookies
    SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
    # SESSION_COOKIE_DOMAIN = os.getenv('SERVER_NAME')  # Set the domain for the cookies
