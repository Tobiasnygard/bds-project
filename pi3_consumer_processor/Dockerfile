FROM python:3.10-slim

# Install dependencies for numpy and tflite
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything including model and labels
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "consumer.py"]
