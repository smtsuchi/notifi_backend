from . import api
from app import db
from ..models import Price, Product, Subscription
from flask import request
from flask_jwt_extended import jwt_required, get_current_user
from ..helpers.web_scrapers import get_product_info_from_url
from ..helpers.send_notifications import send_notifications
from datetime import datetime
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
    else:
        timestamp = datetime.utcnow()
        product_details['last_updated'] = timestamp
        product.from_dict(product_details)
    price = Price(product.id, product_details['price'])
    db.session.add(price)
    
    if product not in user.product_subscriptions.all() \
        or user.subscriptions.filter_by(product_id = product.id)\
            .order_by(desc(Subscription.subscription_date)).first().cancelled_date != None:
        subscription = Subscription(user.id, product.id)
        db.session.add(subscription)
        
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

@api.put('/unsubscribe')
@jwt_required()
def unsubscribe():
    data = request.json
    id = data['id']
    subscription = Subscription.query.get(id)
    subscription.cancel()
    db.session.commit()
    return {
        'status':'ok',
        'message': "Successfully unsubscribed."
    }, 200

@api.get('/subscriptions')
@jwt_required()
def get_subscriptions():
    user = get_current_user()
    return {
        'status': 'ok',
        'message': 'Successfully got subscriptions.',
        'data': user.get_subscriptions()
        }, 200

@api.put('/user/notification-method')
@jwt_required()
def update_notification_method():
    user = get_current_user()
    data = request.json
    user.notification_method = data['notification_method']
    db.session.commit()
    return {
        'status': 'ok',
        'message': 'Successfully updated notification method.',
    }

@api.put('/user/notify-on-drop-only')
@jwt_required()
def update_notify_on_drop_only():
    user = get_current_user()
    data = request.json
    user.notify_on_drop_only = data['notify_on_drop_only']
    db.session.commit()
    return {
        'status': 'ok',
        'message': 'Successfully updated notify tigger.',
        'data': ''
    }

@api.post('/send/emails')
def send_emails():
    products = Product.query.all()
    for product in products:
        product_details = get_product_info_from_url(product.url)
        current_price = product.get_current_price()
        price = Price(product.id, product_details['price'])
        db.session.add(price)
        if current_price != product_details['price']:
            send_notifications(product, current_price, price)
    return {
        'status': 'ok',
        'message': 'Successfully manually triggered and sent emails.
    }

def check_price(url):
    get_product_info_from_url(url)
    