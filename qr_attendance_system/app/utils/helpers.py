import jwt
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import qrcode
from io import BytesIO
import base64

def generate_qr_token():
    """Generate a unique token for QR code"""
    return str(uuid.uuid4())

def generate_qr_code(token):
    """Generate a QR code image from a token"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, 'PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def generate_time_bound_qr(course_id, faculty_id, duration_minutes=3):
    """Generate a time-bound QR code for attendance"""
    token = generate_qr_token()
    expiration = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    return {
        'token': token,
        'expiration': expiration,
        'qr_code': generate_qr_code(token)
    }

def role_required(required_role):
    """Decorator to restrict access based on user role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != required_role:
                return jsonify(msg=f'Missing required role: {required_role}'), 403
            else:
                return fn(*args, **kwargs)
        return decorator
    return wrapper

def roles_required(required_roles):
    """Decorator to restrict access based on multiple user roles"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in required_roles:
                return jsonify(msg=f'Missing required roles: {required_roles}'), 403
            else:
                return fn(*args, **kwargs)
        return decorator
    return wrapper