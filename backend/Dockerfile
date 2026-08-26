# Minimal production Dockerfile for Cloud Run
FROM python:3.11-slim

# Prevent python from buffering stdout/stderr and writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    HOST=0.0.0.0

WORKDIR /app

# Install runtime system packages (curl for healthchecks, ca-certificates for TLS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default Cloud Run container port
EXPOSE 8080

# Cloud Run dynamically assigns PORT environment variable at runtime
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
