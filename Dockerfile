FROM python:3.10-slim

WORKDIR /app

# Good defaults for Django in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install deps first for better layer caching
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install watchdog

# Copy project
COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

RUN useradd -m appuser
USER appuser