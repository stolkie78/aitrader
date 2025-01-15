# Base image
FROM python:3.10-slim

# Werkdirectory instellen
WORKDIR /app

# Vereiste modules kopiëren en installeren
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Python-script kopiëren
COPY aitrader.py /app/aitrader.py
COPY config.json /app/config.json
COPY trader.json /app/trader.json

# Default command instellen
CMD ["python", "aitrader.py"] 