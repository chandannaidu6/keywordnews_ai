# Use the full Python 3.11 image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy only the requirements first (for better caching)
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY app/ ./app/

# Expose the port (if needed)
EXPOSE 8080

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
