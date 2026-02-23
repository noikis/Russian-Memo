FROM python:3.8-slim

WORKDIR /app

# Good defaults for Django in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# (Optional) system deps - keep minimal; add more only if you hit build/runtime errors
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install deps first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements.txt

# Copy project
COPY . /app

EXPOSE 8000
