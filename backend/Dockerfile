# Use an official Python image as base
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements and install them
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the Transformers cache directory to a writable directory
ENV TRANSFORMERS_CACHE=/tmp/cache

# Copy your application code
COPY app/ ./app/

# Expose port 8080 (Lambda expects this port)
EXPOSE 8080

# Run the FastAPI app using uvicorn (production mode)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
