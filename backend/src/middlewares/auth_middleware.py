import jwt
from functools import wraps
from flask import request, jsonify
from backend.src.utils.jwt_util import decode_jwt, get_jwt_secret
from backend.src.models.user_model import User

class UnauthorizedError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class TokenExpiredError(Exception):
    pass

def auth_middleware():
    def middleware_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return jsonify({"error": "Authorization header missing"}), 401
            
            try:
                token = _extract_token(auth_header)
                payload = _validate_token(token)
                _attach_user_to_request(payload)
            except UnauthorizedError as e:
                return jsonify({"error": str(e)}), 401
            except InvalidTokenError as e:
                return jsonify({"error": "Invalid token"}), 403
            except TokenExpiredError as e:
                return jsonify({"error": "Token expired"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return middleware_decorator

def _extract_token(auth_header):
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise UnauthorizedError("Authorization header must be in format 'Bearer token'")
    return parts[1]

def _validate_token(token):
    secret_key = get_jwt_secret()

    payload = decode_jwt(token, secret_key)
    if 'exp' not in payload or _is_token_expired(payload['exp']):
        raise TokenExpiredError("Token has expired")
    return payload

def _is_token_expired(exp):
    import time
    return int(time.time()) > exp

def _attach_user_to_request(payload):
    user_id = payload.get('sub')
    if not user_id:
        raise UnauthorizedError("Token does not contain user information")

    user = User.find_by_id(user_id)
    if not user:
        raise UnauthorizedError("User not found")

    request.user = user


# Role-Based Access Control (RBAC)
def rbac_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not _has_required_role(user, allowed_roles):
                return jsonify({"error": "User does not have the required role"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _has_required_role(user, allowed_roles):
    user_roles = user.get_roles()
    return any(role in user_roles for role in allowed_roles)


# Permissions Middleware
def permissions_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not _has_permission(user, permission):
                return jsonify({"error": "User does not have the required permission"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _has_permission(user, permission):
    user_permissions = user.get_permissions()
    return permission in user_permissions


# Refresh Token Middleware
def refresh_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            return jsonify({"error": "Refresh token missing"}), 401
        
        try:
            secret_key = get_jwt_secret()
            payload = decode_jwt(refresh_token, secret_key)
            if _is_token_expired(payload['exp']):
                return jsonify({"error": "Refresh token expired"}), 403

            _attach_user_to_request(payload)
        except InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 403
        except TokenExpiredError:
            return jsonify({"error": "Refresh token expired"}), 403
        except UnauthorizedError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function


# Token Revocation Middleware
revoked_tokens = set()

def token_revocation_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = _extract_token(auth_header)

        if token in revoked_tokens:
            return jsonify({"error": "Token has been revoked"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def revoke_token(token):
    revoked_tokens.add(token)


# Middleware for 2-Factor Authentication (2FA)
def two_factor_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(request, 'user', None)
        if not user or not user.is_two_factor_auth_enabled() or not _is_two_factor_authenticated(user):
            return jsonify({"error": "Two-factor authentication required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def _is_two_factor_authenticated(user):
    two_factor_token = request.headers.get('X-2FA-Token')
    return two_factor_token and user.two_factor_token == two_factor_token


# Logging Unauthorized Access Attempts
def log_unauthorized_access(user, resource):
    with open('unauthorized_access.log', 'a') as log_file:
        log_file.write(f"Unauthorized access attempt by {user.email} to {resource}\n")