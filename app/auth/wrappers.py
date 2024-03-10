from app import jwt
from ..models import User
from werkzeug.security import check_password_hash
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_jwt_extended import get_jwt_identity

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            return user
        
@basic_auth.error_handler
def basic_auth_error(status):
    return {
        "status": "not ok",
        "message": "Invalid username/password"
        }, status
        
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data['sub']
    user = User.query.get(user_id)
    return user