import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import base64
from urllib.parse import urljoin

# Initialize Kafka producer to send messages to localhost
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def scrape_bing_images():
    base_url = 'https://www.bing.com'
    url = 'https://www.bing.com/images/ideas/sports?nvid=41&FORM=IFPCOD'
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    images = soup.find_all('img')

    for img in images[:100]:
        img_url = img.get('src')
        if not img_url:
            continue
        if img_url.startswith("data:"): # Skip base64 images
            continue
        if img_url.startswith('/'):
            img_url = urljoin(base_url, img_url)
        try:
            img_data = requests.get(img_url).content
            message = {
                'url': img_url,
                'source': 'bing',
                'image_data': base64.b64encode(img_data).decode('utf-8')
            }
            producer.send('sports_images', message)
            print(f"Sent image from {img_url}")
        except Exception as e:
            print(f"Failed to process {img_url}: {e}")
    
    producer.flush()
    producer.close()

scrape_bing_images()
