FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for Playwright and building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies and chromium browser
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "run.py"]
