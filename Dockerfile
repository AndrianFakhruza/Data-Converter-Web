# Gunakan base image Python
FROM python:3.10-slim

# Set workdir di dalam container
WORKDIR /app

# Copy file requirements dan install dependen
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh isi project
COPY . .

# Set environment variable Flask
ENV FLASK_APP=app.py

# Jalankan server pakai gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
