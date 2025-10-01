FROM python:3.9-slim-bullseye
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract4 \
    tesseract-ocr-eng \
    tesseract-ocr-dev
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD gunicorn app:application --bind 0.0.0.0:$PORT