from . import auth
from flask import request, jsonify
from app import db
from ..models import User
from .wrappers import basic_auth
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required

@auth.post('/signup')
def signup_user():
    data = request.json
    username = data['username']
    password = data['password']
    email = data.get('email')
    phone = data.get('phone')

    user = User.query.filter_by(username=username).first()
    if user:
        return {
            'status': 'not ok',
            'message': "That username is already taken."
        }, 400
    user = User.query.filter_by(email=email).first()
    if user:
        return {
            'status': 'not ok',
            'message': "That email is already in use."
        }, 400

    user = User(username, password, email, phone)

    db.session.add(user)
    db.session.commit()

    return {
        'status': 'ok',
        'message': "Successfully created your account!"
    }, 201


@auth.post('/login')
@basic_auth.login_required
def login_user():
    user = basic_auth.current_user()
    access_token = create_access_token(identity=user.id)
    response = jsonify({
        'status': 'ok',
        'user': user.to_dict(),
        'message': "Successfully logged in.",
        'access_token': access_token
    })
    set_access_cookies(response, access_token)
    return response, 200

@auth.post('/logout')
@jwt_required()
def logout_user():
    response = jsonify({
        'status': 'ok',
        'message': "Successfully logged out."
    })
    unset_jwt_cookies(response)
    return response, 200