FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
COPY spotify-exporter.py .

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /app/data

CMD ["python", "spotify-exporter.py", "/app/config.toml"]
