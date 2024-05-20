FROM python:3.9-slim

WORKDIR /app

COPY . .

# Install the dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
# Copy the rest of the application code
COPY . .

# Expose port 8000 for Gunicorn
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
