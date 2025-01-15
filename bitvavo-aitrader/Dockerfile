# Base image
FROM python:3.10-slim

# Werkdirectory instellen
WORKDIR /app

# Vereiste modules kopiëren en installeren
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Python-script kopiëren
COPY aitrader.py /app/trader.py

# Default command instellen
CMD ["python", "trader.py"] 