import jwt
import datetime
from typing import Any, Dict
from flask import current_app, request
from backend.src.models.user_model import User  
from backend.src.config.database_config import db_session 

# In-memory storage for blacklisted tokens
blacklisted_tokens = set()

class JWTUtil:
    """
    Utility class for handling JWT tokens.
    """

    @staticmethod
    def generate_token(payload: Dict[str, Any], expiration_minutes: int = 30) -> str:
        """
        Generate a JWT token with the given payload and expiration time.

        :param payload: The data to include in the JWT token.
        :param expiration_minutes: The time in minutes after which the token will expire.
        :return: Encoded JWT token as a string.
        """
        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)
        payload['exp'] = expiration
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode the JWT token to retrieve the payload.

        :param token: The JWT token to decode.
        :return: Decoded payload as a dictionary.
        :raises: Exception if token is invalid or expired.
        """
        secret_key = current_app.config['JWT_SECRET_KEY']
        decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_payload

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validates the given JWT token.

        :param token: JWT token to validate.
        :return: True if the token is valid, False otherwise.
        """
        try:
            if JWTUtil.is_token_blacklisted(token):
                return False
            JWTUtil.decode_token(token)
            return True
        except Exception:
            return False

    @staticmethod
    def refresh_token(token: str, expiration_minutes: int = 30) -> str:
        """
        Refreshes the JWT token by extending its expiration time.

        :param token: The existing JWT token.
        :param expiration_minutes: New expiration time in minutes.
        :return: A new JWT token with updated expiration.
        """
        decoded_payload = JWTUtil.decode_token(token)
        del decoded_payload['exp']
        return JWTUtil.generate_token(decoded_payload, expiration_minutes)

    @staticmethod
    def extract_claims(token: str, claim: str) -> Any:
        """
        Extract specific claims from the JWT token.

        :param token: The JWT token to extract claims from.
        :param claim: The claim to retrieve from the token.
        :return: Value of the specified claim.
        :raises: Exception if the claim is not found or the token is invalid.
        """
        decoded_payload = JWTUtil.decode_token(token)
        return decoded_payload.get(claim)

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if the token has been blacklisted (useful for logout functionality).

        :param token: The JWT token to check.
        :return: True if the token is blacklisted, False otherwise.
        """
        return token in blacklisted_tokens

    @staticmethod
    def revoke_token(token: str) -> None:
        """
        Revoke the JWT token by blacklisting it.

        :param token: The JWT token to revoke.
        """
        blacklisted_tokens.add(token)


# Usage in an authentication flow

def create_user_token(user_id: str, user_role: str) -> str:
    """
    Generate a JWT token for a user.

    :param user_id: The ID of the user.
    :param user_role: The role of the user.
    :return: JWT token as a string.
    """
    payload = {
        'user_id': user_id,
        'role': user_role,
        'iat': datetime.datetime.utcnow()
    }
    return JWTUtil.generate_token(payload)


def authenticate_user(token: str) -> bool:
    """
    Authenticate the user based on the provided JWT token.

    :param token: The JWT token to authenticate the user.
    :return: True if authentication is successful, False otherwise.
    """
    try:
        if JWTUtil.validate_token(token):
            decoded_payload = JWTUtil.decode_token(token)
            user_id = decoded_payload.get('user_id')
            user = db_session.query(User).filter_by(id=user_id).first()
            if user:
                return True
        return False
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")


def handle_logout(token: str) -> None:
    """
    Handle user logout by revoking the JWT token.

    :param token: The JWT token to revoke.
    """
    try:
        JWTUtil.revoke_token(token)
    except Exception as e:
        raise Exception(f"Logout failed: {str(e)}")


# Middleware to protect routes
def jwt_required(f):
    """
    Decorator to ensure that the route is protected by JWT authentication.
    """
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]  # "Bearer <token>"

        if not token:
            raise Exception("JWT token is missing")
        
        if not JWTUtil.validate_token(token):
            raise Exception("JWT token is invalid or expired")

        return f(*args, **kwargs)
    
    return decorated_function