import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from exceptions import AuthenticationError, AuthorizationError

def generate_token(user_id, username, expiration=24):
    """Generate a JWT token for the given user.
    
    Args:
        user_id (str): The user's ID
        username (str): The user's username
        expiration (int, optional): Token expiration time in hours. Defaults to 24.
    
    Returns:
        str: The JWT token
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiration),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'username': username
    }
    
    return jwt.encode(
        payload,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithm='HS256'
    )

def decode_token(token):
    """Decode a JWT token.
    
    Args:
        token (str): The JWT token to decode
    
    Returns:
        dict: The decoded token payload
    
    Raises:
        AuthenticationError: If the token is invalid or expired
    """
    try:
        return jwt.decode(
            token,
            current_app.config.get('JWT_SECRET_KEY'),
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise AuthenticationError('Invalid token. Please log in again.')

def token_required(f):
    """Decorator to require a valid JWT token for a route.
    
    Args:
        f: The function to decorate
    
    Returns:
        function: The decorated function
    
    Raises:
        AuthenticationError: If no token is provided or the token is invalid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in the header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication required', 'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = decode_token(token)
            # Add user info to the request
            request.user_id = payload['sub']
            request.username = payload['username']
            
        except AuthenticationError as e:
            return jsonify({'error': 'Authentication failed', 'message': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require an admin role for a route.
    
    This decorator should be used after the token_required decorator.
    
    Args:
        f: The function to decorate
    
    Returns:
        function: The decorated function
    
    Raises:
        AuthorizationError: If the user is not an admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # This is a simplified version - in a real app, you would check roles in your database
        # Assuming the token payload has a 'role' field
        # You could also check against a list of admin user IDs
        
        # For demo purposes, we'll use a hardcoded list of admin user IDs
        admin_user_ids = os.environ.get('ADMIN_USER_IDS', '').split(',')
        
        if not hasattr(request, 'user_id') or request.user_id not in admin_user_ids:
            return jsonify({'error': 'Authorization failed', 'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated