import requests as r
import sys
from bs4 import BeautifulSoup

def get_product_info_from_url(url):
    page = r.get(url)
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    soup = BeautifulSoup(page.text, 'lxml')
    product_name = soup.find("span", {"id": "productTitle"}).text.strip()

    price = soup.find('span', class_='a-price')
    whole = price.find('span', class_='a-price-whole')
    cents = price.find('span', class_='a-price-fraction')
    total = float(whole.text + cents.text)

    return {
        'product_name': product_name,
        'price': total,
        'url': url
    }
