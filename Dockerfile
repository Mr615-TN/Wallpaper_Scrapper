# Use the official lightweight Python image
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first
# This optimizes Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create temp directory for wallpaper downloads
RUN mkdir -p /tmp/wallpapers

# Expose the port (Render will override with $PORT env variable)
EXPOSE 5000

# Use shell form to allow environment variable substitution
# Render provides $PORT environment variable (usually 10000)
# Timeout set to 120s for long wallpaper downloads
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 120 app:app
