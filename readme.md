
# Crypto Trading Bot met Dagelijkse Winst/Verlies en Maximum Budget

Deze trading bot is geschreven in Python en maakt gebruik van de Bitvavo API. Het bevat functies om meerdere munten te volgen, dagelijkse winst/verlies te berekenen en transacties te beheren binnen een maximum investeringsbudget.

---

## **Functionaliteiten**

1. **Dagelijkse winst/verlies berekening**
   - Berekening van winst/verlies per munt aan de hand van transacties (aankoop/verkoop).

2. **Prijsvoorspellingen**
   - Gebruikt een lineair regressiemodel om toekomstige prijzen te voorspellen op basis van historische data.

3. **Maximum totaal investeringsbedrag**
   - Zorgt ervoor dat het totale geïnvesteerde bedrag nooit hoger wordt dan een vooraf bepaald maximum (`MAX_TOTAL_INVESTMENT`).

4. **Dagelijkse rapportage**
   - Aan het einde van elke dag wordt een overzicht gegeven van de winst/verlies situatie voor elke munt.

---

## **Configuratie**

### Vereisten
- **Python 3.7+**
- Geïnstalleerde pakketten:
  - `bitvavo`
  - `scikit-learn`
  - `numpy`


### API-sleutels
Voeg je Bitvavo API-sleutels toe in de configuratie:
```python
API_KEY = 'jouw_api_key'
API_SECRET = 'jouw_api_secret'
```

### Instellingen
De belangrijkste configuraties die je kunt aanpassen:
- **`SYMBOLS`**: Lijst van te volgen munten (bijv. `['BTC-EUR', 'ETH-EUR', 'XRP-EUR']`).
- **`WINDOW_SIZE`**: Aantal historische datapunten voor het trainen van het voorspellingsmodel.
- **`THRESHOLD`**: Percentage voorspelde prijsverandering voor koop/verkoopacties.
- **`MAX_TOTAL_INVESTMENT`**: Maximum totaal bedrag in EUR dat mag worden geïnvesteerd.

---

## **Hoe werkt de bot?**

1. **Prijs ophalen**
   - De bot haalt de actuele prijs van elke munt op via de Bitvavo API.

2. **Prijsvoorspelling**
   - Een lineair regressiemodel wordt getraind met `WINDOW_SIZE` datapunten en gebruikt om de volgende prijs te voorspellen.

3. **Beslissingen nemen**
   - **Koop**: Als de voorspelde prijsstijging groter is dan `THRESHOLD` en er budget beschikbaar is.
   - **Verkoop**: Als de voorspelde prijsdaling groter is dan `THRESHOLD`.

4. **Dagelijkse rapportage**
   - Aan het einde van de dag wordt een overzicht gegeven van de winst/verlies situatie per munt.

---

## **Codefragment**

Hier is een fragment van de belangrijkste instellingen:
```python
# Configuratie
SYMBOLS = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR']
WINDOW_SIZE = 10  # Historische datapunten voor analyse
THRESHOLD = 2  # Percentage prijsverandering voor acties
MAX_TOTAL_INVESTMENT = 1000  # Maximum investeringsbedrag
```

---

## **Installatie**

apt install python3-full 

python3 -m venv aitrader_runtime
in Bash_profile: source $HOME/aitrader_runtime/bin/activate


1. Installeer de benodigde pakketten:
   ```bash
   pip install python-bitvavo-api scikit-learn numpy
   ```

2. Voeg je API-sleutels toe aan de configuratie in het script.

3. Start de bot:
   ```bash
   python trading_bot.py
   ```

---

## **Uitbreidingsmogelijkheden**

1. **Geavanceerdere modellen**
   - Gebruik meer geavanceerde AI-technieken zoals LSTM of Random Forest.

2. **Technische indicatoren**
   - Integreer indicatoren zoals RSI, MACD of Bollinger Bands.

3. **Notificaties**
   - Voeg meldingen toe via e-mail, Telegram of andere platforms.

---

## **Disclaimer**

Deze bot is bedoeld voor educatieve doeleinden. Handel met voorzichtigheid en begrijp de risico's van crypto-investeringen. Gebruik altijd bedragen die je bereid bent te verliezen.
# aitrader
