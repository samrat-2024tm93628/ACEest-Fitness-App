# Use an optimized, slim Python image for efficiency [cite: 40]
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Command to launch the API
CMD ["python", "app.py"]