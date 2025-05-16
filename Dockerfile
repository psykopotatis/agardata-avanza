FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port Flask/Gunicorn will run on
EXPOSE 5000

# Use Gunicorn as the production WSGI server
# Bind to the PORT env var if provided (Railway sets PORT), fallback to 5000
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2