import random
import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import base64
from urllib.parse import urljoin, urlparse
import hashlib
import time
import urllib3
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sent_hashes = set()

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def hash_image(image_data):
    return hashlib.md5(image_data).hexdigest()

def is_valid_image_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and not url.lower().endswith('.svg')

def get_image_data(url):
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception:
        return None

def scrape_images_and_send():
    search_terms = ['sports', 'tennis', 'football', 'basketball', 'swimming']
    query = random.choice(search_terms)
    url = f'https://www.bing.com/images/search?q={query}&form=HDRSC3'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        images = soup.find_all('img')
    except Exception as e:
        print(f"❌ Failed to fetch or parse the page: {e}")
        return

    new_images_sent = 0
    for img in images:
        if new_images_sent >= 10:
            break

        img_url = img.get('src') or img.get('data-src')
        if not img_url:
            continue

        if img_url.startswith('/'):
            img_url = urljoin(url, img_url)

        if not is_valid_image_url(img_url):
            continue

        image_data = get_image_data(img_url)
        if not image_data or len(image_data) < 1024:
            print(f"[⚠️] Skipped small/broken image: {img_url} ({len(image_data) if image_data else 0} bytes)")
            continue

        img_hash = hash_image(image_data)
        if img_hash in sent_hashes:
            print(f"[⏩] Skipped duplicate image: {img_url}")
            continue

        message = {
            'url': img_url,
            'source': 'bing',
            'image_data': base64.b64encode(image_data).decode('utf-8')
        }
        try:
            producer.send('sports_images', message)
            sent_hashes.add(img_hash)
            new_images_sent += 1
            print(f"✅ Sent to kafka: {img_url}")
        except Exception as e:
            print(f"[❌] Failed to send image: {e}")

def run_periodic_scraper(interval=600):
    while True:
        print("\n🚀 Starting new scraping cycle...")
        scrape_images_and_send()
        print(f"😴 Cycle completed. Sleeping for {interval} seconds....\n")
        time.sleep(interval)

run_periodic_scraper(interval=10)
