import requests as r
import sys
from bs4 import BeautifulSoup

def get_product_info_from_url(url):
    page = r.get(url)
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    soup = BeautifulSoup(page.text, 'lxml')

    product_name_element = soup.find("span", {"id": "productTitle"})
    product_name = product_name_element.text.strip() if product_name_element else None

    try:
        price_element = soup.select_one('span.a-offscreen')
        price = float(price_element.text.strip('$ '))
    except:
        price_element = soup.find('span', class_='a-price')
        whole = price_element.find('span', class_='a-price-whole')
        cents = price_element.find('span', class_='a-price-fraction')
        price = float(whole.text + cents.text)

    image_element = soup.select_one("#landingImage")
    image = image_element.attrs.get("src") if image_element else None

    description_element = soup.select_one("#productDescription")
    description = description_element.text.strip() if description_element else None
    print(product_name, price)
    return {
        'product_name': product_name,
        'price': price,
        'url': url,
        'image_url': image,
        'description': description,
    }
