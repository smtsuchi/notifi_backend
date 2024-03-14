from app import db
from flask import render_template
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from twilio.rest import Client
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models import Log

# TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
# TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
# SEND_GRID_API_KEY = os.environ.get('SEND_GRID_API_KEY')
GOOGLE_APP_PASSWORD = os.environ.get('GOOGLE_APP_PASSWORD')
GOOGLE_EMAIL_SENDER = os.environ.get('GOOGLE_EMAIL_SENDER')
# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# sg = SendGridAPIClient(SEND_GRID_API_KEY)


def send_gmails(subscribers, product, old_price, new_price):
    GOOGLE_EMAIL_SENDER
    message = MIMEMultipart("alternative")
    text = f"""\
Hello!
Here is the price update for the product: { product.product_name }
The price went {"UP" if new_price.amount > old_price else "DOWN"}!
From ${ old_price } to ${ new_price.amount }."""
    html = render_template(
        'email_template.html',
        product=product,
        old_price=old_price,
        new_price=new_price.amount
    )
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message["Subject"] = "New Price Alert from NotiFi"
    message["From"] = GOOGLE_EMAIL_SENDER
    message.attach(part1)
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(GOOGLE_EMAIL_SENDER, GOOGLE_APP_PASSWORD)
        for subscriber in subscribers:
            message["To"] = subscriber.email
            server.sendmail(GOOGLE_EMAIL_SENDER, subscriber.email, message.as_string())
            log = Log(subscriber.id, new_price.id, 'email')
            db.session.add(log)
        db.session.commit()
        
# def send_sg_emails(subscribers, product, old_price, new_price):
#     for subscriber in subscribers:
#         message = Mail(
#             from_email=GOOGLE_EMAIL_SENDER,
#             to_emails=subscriber.email,
#             subject='New Price Alert',
#             html_content=render_template(
#                 'email_template.html',
#                 product=product,
#                 old_price=old_price,
#                 new_price=new_price.amount
#             )
#         )
#         response = sg.send(message)
#         if response.status_code == 202:
#             log = Log(subscriber.id, new_price.id, 'email')
#             db.session.add(log)
#             db.session.commit()  

# def send_twilio_sms(subscribers, product, old_price, new_price):
#     for subscriber in subscribers:
#         message = client.messages.create(
#             from_='+18559652446',
#             body=f'Hello from NotiFi!\n Your product {product.product_name} has gone {"up" if new_price.amount > old_price else "down"} in price.\nThe old price was : ${old_price} and the new price is ${new_price.amount}',
#             to=f'+1{subscriber.phone}'
#         )
#         if not message.sid.error_code:
#             log = Log(subscriber.id, new_price.id, 'phone')
#             db.session.add(log)
#             db.session.commit()
        
def send_notifications(product, old_price, new_price):
    email_list = []
    sms_list = []
    for subscriber in product.subscribers:
        if subscriber.notify_on_drop_only and new_price.amount >= old_price:
            continue
        if subscriber.notification_method == "both":
            email_list.append(subscriber)
            sms_list.append(subscriber)
        elif subscriber.notification_method == "email":
            email_list.append(subscriber)
        elif subscriber.notification_method == "sms":
            sms_list.append(subscriber)

    send_gmails(email_list, product, old_price, new_price)
    # send_twilio_sms(sms_list, product, old_price, new_price) #Blocked by Twillio A2P 10DLC Regulations
