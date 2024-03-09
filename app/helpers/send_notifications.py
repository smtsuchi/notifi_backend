from ..models import Product
from sendgrid import SendGridAPIClient
from twilio.rest import Client
import json
import os

sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
NOTIFY_SERVICE_SID = os.environ.get('NOTIFY_SERVICE_SID')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_emails(emails, product):
    data = {
        "personalizations": [{
            "to": [{"email": email} for email in emails],
            "subject": "Sending with SendGrid is Fun"
        }],
        "from": {
            "email": "test@example.com"
        },
        "content": [{
            "type": "text/plain",
            "value": "and easy to do anywhere, even with Python"
        }]
    }
    sg.client.mail.send.post(request_body=data)
    

def send_sms(phone_numbers, product):
    # https://www.twilio.com/docs/notify/quickstart/sms
    notification = client.notify.services(NOTIFY_SERVICE_SID) \
        .notifications.create(
            body='',
            to_bindings = [json.dumps({"binding_type": "sms", "address": number}) for number in phone_numbers],
        )

def send_notifications(product_id, amount):
    product = Product.query.get(product_id)
    email_list = []
    sms_list = []
    for subscriber in product.subscribers:
        if subscriber.notification_method == "both":
            email_list.append(subscriber.email)
            sms_list.append(subscriber.phone)
        elif subscriber.notification_method == "email":
            email_list.append(subscriber.email)
        elif subscriber.notification_method == "sms":
            sms_list.append(subscriber.phone)
    send_emails(email_list, product)
    send_sms(sms_list, product)
