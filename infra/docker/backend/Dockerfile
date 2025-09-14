# Minimal backend Dockerfile for legacy Django app
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install project dependencies (fallback to legacy app runtime deps)
COPY backend/requirements /tmp/requirements
RUN pip install --no-cache-dir -r /tmp/requirements/dev.txt || true

# Also try installing deps from legacy app if present
RUN mkdir -p "/tmp/legacy"
COPY ["src/student_auth/", "/tmp/legacy/"]
RUN if [ -f "/tmp/legacy/requirements.txt" ]; then pip install --no-cache-dir -r "/tmp/legacy/requirements.txt"; fi || true

COPY . /workspace

# Fix line endings for shell scripts
RUN find /workspace -name "*.sh" -exec dos2unix {} \;

EXPOSE 8000
CMD ["python", "src/student_auth/manage.py", "runserver", "0.0.0.0:8000"]
