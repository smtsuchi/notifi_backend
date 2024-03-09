from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import desc, func
from app import db
from uuid import uuid4
from .helpers.send_notifications import send_notifications

subscription = db.Table('subscription',
    db.Column('user_id', db.String, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, primary_key=True),
    db.Column('product_id', db.String, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False, primary_key=True),
    db.Column('subscription_date', db.DateTime, nullable=False, default=datetime.utcnow()),
    )

class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    amount = db.Column(db.Numeric)

    def __init__(self, product_id, amount):
        self.product_id = product_id
        self.amount = amount

        send_notifications(product_id, amount)

    def update_timestamp(self):
        self.timestamp = datetime.utcnow()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    product_name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    prices = db.relationship("Price", backref='product', lazy='dynamic')

    def __init__(self, url='', product_name=''):
        self.id = "prod_" + str(uuid4())
        self.url = url
        self.product_name = product_name

    def get_subscriber_count(self):
        return len(self.subscribers)
    
    def get_last_checked(self):
        price_obj = self.prices.order_by(desc(Price.timestamp)).first()
        return price_obj.timestamp

    def from_dict(self, product_details):
        self.url = product_details['url']
        self.product_name = product_details['product_name']
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'product_name': self.product_name,
            'last_checked': self.get_last_checked(),
            'date_created': self.date_created,
            'subscriber_count': self.get_subscriber_count(),
            # TODO
            'current_price': '',
            'lowest_recorded_price': '',
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
    subscriptions = db.relationship("Product", secondary=subscription, backref='subscribers')

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
        subscriptions = (
            db.session.query(
                subscription.c.subscription_date,
                Product.id.label('product_id'),
                Product.url.label('product_url'),
                Product.product_name.label('product_name'),
                func.max(Price.amount).label('latest_price'),
                func.max(Price.timestamp).label('last_checked')
            )
            .join(Product, subscription.c.product_id == Product.id)
            .outerjoin(Price, (Product.id == Price.product_id))
            .filter(subscription.c.user_id == self.id)
            .group_by(subscription.c.subscription_date, Product.id)
            .order_by(subscription.c.subscription_date.desc())
            .all()
        )
        subscriptions_list = []
        for s in subscriptions:
            subscription_dict = {
                'subscription_date': s.subscription_date,
                'product_id': s.product_id,
                'product_url': s.product_url,
                'product_name': s.product_name,
                'latest_price': float(s.latest_price),
                'last_checked': s.last_checked,
            }
            subscriptions_list.append(subscription_dict)
        return subscriptions_list

    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'date_created': self.date_created,
            'subscription_count': len(self.subscriptions),
            'notify_on_drop_only': self.notify_on_drop_only
        }
        





class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id', ondelete='CASCADE'), nullable=False)
    notification_method = db.Column(db.String, nullable=False)

    def __init__(self, user_id, price_id, notification_method):
        self.user_id = user_id
        self.price_id = price_id
        self.notification_method = notification_method
        
