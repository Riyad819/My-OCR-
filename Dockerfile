FROM python:3.9-slim-bullseye

# Set up environment variables for Tesseract download
ENV TESSERACT_VERSION 5.3.4
ENV TESSDATA_VERSION 4.1.0

# Install necessary system dependencies (wget for downloading) and Tesseract itself
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tesseract-ocr \
    tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD gunicorn single_app:application --bind 0.0.0.0:$PORT