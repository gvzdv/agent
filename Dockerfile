FROM python:3.12-slim

# Environment variables

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]