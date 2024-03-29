from app import scheduler, db
from ..models import Price, Product
from ..helpers.web_scrapers import get_product_info_from_url
from ..helpers.send_notifications import send_notifications

@scheduler.task('interval', id='scrape_products', hours=0, minutes=30, misfire_grace_time=900)
def scrape_products():
    with scheduler.app.app_context():
        products = Product.query.all()
        failed = []
        for product in products:
            product_details = get_product_info_from_url(product.url)
            if product_details[0].get('status') == 'not ok':
                failed.append(product.url)
                continue
            current_price = product.get_current_price()
            price = Price(product.id, product_details[0]['price'])
            db.session.add(price)
            if current_price != product_details[0]['price']:
                send_notifications(product, current_price, price)
        db.session.commit()
        print("FAILED SCHEDULE:", failed)
    print('This job is executed every 30 minutes.')