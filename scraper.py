# scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

def scrape_jumia(base_url, max_pages=25):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    all_products = []

    for page in range(1, max_pages + 1):
        if "?" in base_url:
            url = f"{base_url}&page={page}"
        else:
            url = f"{base_url}?page={page}"

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, 'lxml')
        products = soup.find_all('article', class_='prd') + soup.find_all('div', class_='sku -gallery')

        if not products:
            break

        for product in products:
            # --- Name ---
            name_tag = product.find('h3', class_='name')  or product.find('div', class_='name')
            if name_tag:
                name = name_tag.text.strip()
            else:
                continue # skip product if no name found

            # --- Price (check discounted & old) ---
            price_tag = product.find('div', class_='prc') or product.find('div', class_='old')
            if price_tag:
                price_text = price_tag.text.strip().replace('₦', '').replace(',', '')
                try:
                    price = int(price_text)
                except:
                    price = None
            else:
                price = None

            # --- Rating (convert to float) ---
            rating_tag = product.find('div', class_='stars _s')
            if rating_tag and rating_tag.text.strip():
                try:
                    rating = float(rating_tag.text.strip().split()[0])
                except:
                    rating = None
            else:
                rating = None

            all_products.append({
                "Product Name": name,
                "Price (NGN)": price,
                "Rating": rating
            })

        time.sleep(random.uniform(2, 5))  # polite delay

    return pd.DataFrame(all_products)
