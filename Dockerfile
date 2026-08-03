# Production Dockerfile for Astra OS Backend Runtime
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specification
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app /app/app
COPY main.py .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
