from kafka import KafkaProducer
import scrapy
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

class SportsImageSpider(scrapy.Spider):
    name = 'sports_images'
    start_urls = ['https://www.bing.com/images/search?q=sports']

    def parse(self, response):
        for img in response.css('img'):
            image_url = img.attrib.get('src')
            if image_url:
                producer.send('raw-images', {'url': image_url})
