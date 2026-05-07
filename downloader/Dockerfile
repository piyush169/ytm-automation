# Use a slim Python image to keep the final footprint small
FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure logs are sent to the terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# - ffmpeg: Required for audio conversion and tagging
# - curl: For system health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies 
# We install these directly to ensure the latest yt-dlp is fetched
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    requests \
    pydantic \
    yt-dlp

# Copy your application code
COPY app.py .

# Create the storage directory and ensure it has correct permissions
# This should be mapped to a volume in your docker-compose file
RUN mkdir -p /music && chmod 777 /music

# Expose the API port
EXPOSE 8000

# Run the API with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
