FROM python:3.13.1-slim

ENV PYTHONUNBUFFERED=1

# Vereiste modules kopiëren en installeren
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Python-script kopiëren
COPY hodl.py /app/hodl.py

# Volume aanmaken voor data
VOLUME /app/data

# Default command instellen
CMD ["python", "hodl.py"] 