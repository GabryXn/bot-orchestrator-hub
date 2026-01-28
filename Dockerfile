# Use the official lightweight Python image
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=True

# Set working directory
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run uses port 8080 by default
ENV PORT=8080
EXPOSE 8080

# Run the web service with uvicorn
# Use 1 worker for free tier (scale via Cloud Run instances instead)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
