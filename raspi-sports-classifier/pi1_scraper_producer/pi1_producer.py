import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import base64

producer = KafkaProducer(
    bootstrap_servers=['<pi3_ip>:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def scrape_bing_images():
    url = 'https://www.bing.com/images/search?q=sports&go=Søk&qs=n&form=QBIR&sp=-1&lq=0&pq=sports&sc=10-6&cvid=C44EF7C075514D1F814D05CFF97804E4&first=1'
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    images = soup.find_all('img')

    for img in images[:10]:
        img_url = img.get('src')
        if not img_url:
            continue
        img_data = requests.get(img_url).content
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        metadata = {
            "url": img_url,
            "source": "bing",
            "image": encoded_img
        }
        producer.send('sports_images', metadata)
        print(f"Sent image from {img_url}")

scrape_bing_images()