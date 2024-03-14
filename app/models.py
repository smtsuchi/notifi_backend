from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import asc, desc
from app import db
from uuid import uuid4

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.String, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    subscription_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    cancelled_date = db.Column(db.DateTime)
    
    def __init__(self, user_id, product_id):
        self.id = "sub_" + str(uuid4())
        self.user_id = user_id
        self.product_id = product_id

    def to_dict(self):
        p = Product.query.get(self.product_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'subscription_date': self.subscription_date,
            'cancelled_date': self.cancelled_date,
            'product': p.to_dict()
        }
    
    def cancel(self):
        self.cancelled_date = datetime.now(datetime.UTC)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    product_name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    description = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    last_updated = db.Column(db.DateTime)
    prices = db.relationship("Price", backref='product', lazy='dynamic')

    def __init__(self, url='', product_name='', image_url='', description=''):
        self.id = "prod_" + str(uuid4())
        self.url = url
        self.product_name = product_name
        self.image_url = image_url
        self.description = description
    
    def get_prices(self):
        prices =  self.prices.order_by(desc(Price.timestamp)).all()
        return [p.to_dict() for p in prices]

    def get_subscriber_count(self):
        return len(self.subscribers)
    
    def get_last_checked(self):
        price_obj = self.prices.order_by(desc(Price.timestamp)).first()
        return price_obj.timestamp
    
    def get_current_price(self):
        price_obj = self.prices.order_by(desc(Price.timestamp)).first()
        return float(price_obj.amount)
    
    def get_lowest_recorded_price(self):
        price_obj = self.prices.order_by(asc(Price.amount)).first()
        return float(price_obj.amount)

    def from_dict(self, product_details):
        self.url = product_details['url']
        self.product_name = product_details['product_name']
        self.image_url = product_details['image_url']
        self.description = product_details['description']
        self.last_updated = product_details.get('last_updated')
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'product_name': self.product_name,
            'image_url': self.image_url,
            'description': self.description,
            'last_checked': self.get_last_checked(),
            'date_created': self.date_created,
            'last_updated': self.last_updated,
            'subscriber_count': self.get_subscriber_count(),
            'current_price': self.get_current_price(),
            'lowest_recorded_price': self.get_lowest_recorded_price(),
        }

class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    amount = db.Column(db.Numeric)

    def __init__(self, product_id, amount):
        self.product_id = product_id
        self.amount = amount

    def update_timestamp(self):
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'price_id': self.id,
            'timestamp': self.timestamp,
            'amount': self.amount,
        }



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    notification_method = db.Column(db.String, nullable=False, default='email')
    notify_on_drop_only = db.Column(db.Boolean, nullable=False, default=False)
    product_subscriptions = db.relationship("Product", secondary="subscription", backref='subscribers', lazy='dynamic')
    subscriptions = db.relationship("Subscription", backref='user', viewonly=True, lazy='dynamic')

    def __init__(self, username, password, email, phone):
        self.id = uuid4()
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.phone = phone

    def get_following(self):
        following_set = {u.id for u in self.following}
        return following_set
    
    def get_subscriptions(self):
        subscriptions_list = []
        for s in self.subscriptions.order_by(desc(Subscription.subscription_date)).all():
            if not s.cancelled_date:
                subscription_dict = s.to_dict()
                subscriptions_list.append(subscription_dict)
        return subscriptions_list
    
    def edit_profile(self, changes):
        self.username = changes['username']
        self.email = changes['email']
        self.phone = changes['phone']
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'date_created': self.date_created,
            'subscription_count': len(self.subscriptions.all()),
            'notify_on_drop_only': self.notify_on_drop_only,
            'notification_method': self.notification_method
        }

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id', ondelete='CASCADE'), nullable=False)
    notification_method = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, user_id, price_id, notification_method):
        self.user_id = user_id
        self.price_id = price_id
        self.notification_method = notification_method
        
