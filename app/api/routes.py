from . import api
from app import db
from ..models import Price, Product, User
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from .web_scrapers import get_product_info_from_url
from sqlalchemy import desc

@api.post('/subscribe')
@jwt_required()
def subscribe():
    data = request.json
    user = get_current_user()

    url = data['url']
    product_details = get_product_info_from_url(url)
    product = Product.query.filter_by(url=url).first()

    if not product:
        product = Product()
        product.from_dict(product_details)
        db.session.add(product)
        price = Price(product.id, product_details['price'])
        db.session.add(price)
    else:
        price = Price.query.filter_by(product_id=product.id).order_by(desc(Price.timestamp)).first()
        if price.amount == product_details['price']:
            price.update_timestamp()
        else:
            # tigger notifs
            price = Price(product.id, product_details['price'])
            db.session.add(price)
    
    if product not in user.subscriptions:
        user.subscriptions.append(product)
        
        response = {
        'status':'ok',
        'message': "Successfully subscribed."
    }, 201
    else:
        response = {
            'status': 'not ok',
            'message': "You are already subscribed to this product."
        }, 400
    db.session.commit()
    return response

@api.get('/subscriptions')
@jwt_required()
def get_subscriptions():
    user = get_current_user()
    return {
        'status': 'ok',
        'message': 'Successfully got subscriptions.',
        'data': user.get_subscriptions()
        }, 200

def check_price(url):
    get_product_info_from_url(url)
    