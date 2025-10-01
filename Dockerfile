FROM python:3.9-slim-bullseye

# Tesseract installation removed here to fix Exit Code 100 error.
# Tesseract will be handled via the updated requirements.txt

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD gunicorn single_app:application --bind 0.0.0.0:$PORT