# Use the newest stable lightweight official Python image (3.14-slim)
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first
# This optimizes Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the application runs on (default for Flask/Gunicorn)
EXPOSE 5000

# Define the command to run the application using Gunicorn (the production WSGI server).
# Gunicorn will listen on port 5000 inside the container.
# Change 'app:app' if your Flask application instance is named differently or in a different file.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
