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

**How to run the project (locally)**

The project is dockerized, so please download docker desktop if you do not already have it installed. https://www.docker.com/products/docker-desktop/

1. Start up docker desktop on your computer.

2. Open a terminal and run docker-compose up --build

Wait until the project is built (when the terminal stops spitting out new lines)

3. Open a new terminal and run docker-compose up consumer

Check the output in the terminal, you might have to re-run the command if the consumer runs into an issue with the kafka topic, but restarting it should fix it.

4. Open a new terminal and run docker-compose up scraper

Everything should be up and running on http://localhost:6969

If there are any issues you can run docker-compose ps -a to check all running and stopped containers. If any containers are stopped, simply restart them by doing docker-compose up *container name*

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
