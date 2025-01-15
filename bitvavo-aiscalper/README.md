
# Bitvavo Scalping Trading Bot

Deze trading bot is ontwikkeld om daytrading mogelijk te maken op het Bitvavo-platform. De bot gebruikt configuratiebestanden (`config.json` en `trader.json`) om API-sleutels, handelsparameters en andere instellingen te laden. De bot ondersteunt een demo-modus waarin trades worden gesimuleerd zonder echte transacties uit te voeren.

---

## Inhoud

- [Functies](#functies)
- [Vereisten](#vereisten)
- [Installatie](#installatie)
- [Gebruik](#gebruik)
- [Configuratiebestanden](#configuratiebestanden)
- [Docker-gebruik](#docker-gebruik)

---

## Functies

- Verbinden met de Bitvavo API.
- Automatisch kopen en verkopen van cryptocurrency op basis van vooraf ingestelde parameters.
- Ondersteuning voor een demo-modus voor simulaties.
- Logging met tijdstempels voor eenvoudige debugging.

---

## Vereisten

- **Python**: 3.8 of hoger
- **Modules**:
  - `python-bitvavo-api`
  - `json`
  - `datetime`
  - `time`

---

## Installatie

1. **Clone de repository**:
   ```bash
   git clone https://github.com/jouw-repo/bitvavo-trading-bot.git
   cd bitvavo-trading-bot
   ```

2. **Installeer de vereisten**:
   ```bash
   pip install python-bitvavo-api
   ```

3. **Voeg configuratiebestanden toe**:
   Maak `config.json` en `trader.json` aan in de projectmap (zie [Configuratiebestanden](#configuratiebestanden)).

---

## Gebruik

Start de bot met:
```bash
python trading_bot.py
```

Om de bot in demo-modus uit te voeren (standaard geconfigureerd), stel je `DEMO_MODE` in op `true` in `trader.json`.

---

## Configuratiebestanden

### `config.json`

Dit bestand bevat je Bitvavo API-sleutels en andere instellingen.

```json
{
  "API_KEY": "jouw_api_key",
  "API_SECRET": "jouw_api_secret",
  "RESTURL": "https://api.bitvavo.com/v2",
  "WSURL": "wss://ws.bitvavo.com/v2/",
  "ACCESSWINDOW": 10000,
  "DEBUGGING": false
}
```

### `trader.json`

Dit bestand bevat de handelsparameters.

```json
{
  "SYMBOLS": ["BTC-EUR", "ETH-EUR", "XRP-EUR"],
  "WINDOW_SIZE": 10,
  "THRESHOLD": 2,
  "MAX_TOTAL_INVESTMENT": 1000,
  "current_investment": 0,
  "DAILY_DATA": {
    "BTC-EUR": {"transactions": [], "prices": []},
    "ETH-EUR": {"transactions": [], "prices": []},
    "XRP-EUR": {"transactions": [], "prices": []}
  },
  "START_TIME": 1700000000.0,
  "DEMO_MODE": true,
  "SLEEP_INTERVAL": 3600
}
```

---

## Docker-gebruik

1. **Bouw de Docker-image**:
   Gebruik de volgende Dockerfile om de image te bouwen:

   ```dockerfile
   # Base image
   FROM python:3.10-slim

   # Werkdirectory instellen
   WORKDIR /app

   # Vereiste modules kopiëren en installeren
   COPY requirements.txt /app/requirements.txt
   RUN pip install --no-cache-dir -r requirements.txt

   # Configuratie- en Python-script kopiëren
   COPY config.json /app/config.json
   COPY trader.json /app/trader.json
   COPY trading_bot.py /app/trading_bot.py

   # Default command instellen
   CMD ["python", "trading_bot.py"]
   ```

   Bouw de image:
   ```bash
   docker build -t aiscalper:0.1 .
   ```

2. **Start de container**:
   ```bash
   docker run -v $(pwd)/config.json:/app/config.json -v $(pwd)/trader.json:/app/trader.json aiscalper:0.1
   ```

In de bovenstaande commando's wordt aangenomen dat de configuratiebestanden (`config.json` en `trader.json`) zich in de huidige directory bevinden.

---

## Disclaimer

Deze bot is bedoeld voor educatieve doeleinden. Gebruik op eigen risico.
