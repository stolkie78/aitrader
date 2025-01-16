FROM python:3.13.1-slim

ENV PYTHONUNBUFFERED=1

# Vereiste modules kopiëren en installeren
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Python-script kopiëren
COPY trader.py /app/trader.py

# Default command instellen
CMD ["python", "trader.py"] 