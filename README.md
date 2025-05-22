# 🖼️ Raspberry Pi Distributed Image Processing Pipeline

This project sets up a distributed system for web scraping, image classification, and metadata management using Docker containers. It's designed for deployment across a cluster of Raspberry Pis, but can be tested locally using Docker Compose.

---

## 📦 Components

| Service       | Description                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------- |
| **Scraper**   | Uses Scrapy to crawl sports images and sends them to Kafka.                                    |
| **Kafka**     | Acts as the message broker for image data.                                                     |
| **Consumer**  | Receives images from Kafka, classifies them using an AI model, and stores metadata in MariaDB. |
| **MariaDB**   | Stores metadata about each image: filename, label, and file path.                              |
| **Flask App** | Displays classified image metadata in a simple web interface.                                  |

---

To build and start all services run from root folder:

docker-compose up --build

---

**Tech Stack**

Python 3.10

Scrapy (for crawling)

Kafka + Zookeeper (data flow)

TensorFlow or PyTorch (AI model)

Flask (web frontend)

MariaDB (metadata storage)

Docker + Docker Compose

---
