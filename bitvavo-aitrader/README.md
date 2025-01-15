
# Eenvoudige Trading Bot met AI Predictie en RSI

Deze eenvoudige trading bot gebruikt **AI-predictie (lineaire regressie)** en **RSI (Relative Strength Index)** om koop- en verkoopsignalen te genereren. Het script haalt marktprijzen op via de Bitvavo API, berekent RSI en voorspelt toekomstige prijzen op basis van historische data.

---

## Functies van de Bot

1. **Prijs ophalen**: De bot haalt de actuele marktprijs op voor het opgegeven handelspaar.
2. **RSI berekenen**: De bot berekent RSI (Relative Strength Index) om overbought- en oversold-condities te detecteren.
3. **AI-predictie**: Gebruikt lineaire regressie om de toekomstige prijs te voorspellen.
4. **Koop- en verkoopsignalen**:
   - **Koop** als:
     - RSI < `RSI_OVERSOLD`
     - Voorspelde prijswijziging > `THRESHOLD`
   - **Verkoop** als:
     - RSI > `RSI_OVERBOUGHT`
     - Voorspelde prijswijziging < `-THRESHOLD`
5. **Logging per functionaliteit**: Elke belangrijke stap wordt gelogd, inclusief prijzen, RSI, voorspellingen, en beslissingen.

---

## Configuratiebestand (`trader.json`)

De bot gebruikt een JSON-configuratiebestand om de belangrijkste parameters in te stellen:

```json
{
    "SYMBOL": "BTC-EUR",                // Handelspaar (bijv. Bitcoin/Euro)
    "WINDOW_SIZE": 14,                 // Aantal periodes voor RSI-berekening
    "THRESHOLD": 0.5,                  // Drempel voor voorspelde prijsverandering (%)
    "TRADE_AMOUNT": 0.01,              // Hoeveelheid munt per trade
    "RSI_OVERBOUGHT": 70,              // RSI-drempel voor overbought (verkoop)
    "RSI_OVERSOLD": 30,                // RSI-drempel voor oversold (koop)
    "DEMO_MODE": true,                 // Simulatiemodus (geen echte trades)
    "CHECK_INTERVAL": 60               // Tijd (in seconden) tussen controles
}
```

### Uitleg van de parameters

- **SYMBOL**: Het handelspaar dat de bot moet volgen, zoals `BTC-EUR` (Bitcoin/Euro).
- **WINDOW_SIZE**: Het aantal periodes dat wordt gebruikt voor de berekening van RSI.
- **THRESHOLD**: De drempelwaarde voor voorspelde prijsveranderingen (in procenten).
- **TRADE_AMOUNT**: De hoeveelheid cryptovaluta die wordt verhandeld per transactie.
- **RSI_OVERBOUGHT**: De RSI-waarde waarboven de markt als overbought wordt beschouwd (verkoopsignaal).
- **RSI_OVERSOLD**: De RSI-waarde waaronder de markt als oversold wordt beschouwd (koopsignaal).
- **DEMO_MODE**: Als `true`, voert de bot geen echte transacties uit en logt alleen simulaties.
- **CHECK_INTERVAL**: Het tijdsinterval (in seconden) tussen opeenvolgende marktcontroles.

---

## Voorbeeld Log

Bij uitvoering van de bot worden de volgende logregels weergegeven:

```
[2025-01-15 16:30:00] Trading bot gestart voor BTC-EUR.
[2025-01-15 16:31:00] Ophalen van actuele prijs voor BTC-EUR.
[2025-01-15 16:31:00] Berekenen van RSI.
[2025-01-15 16:31:00] AI-model trainen met historische prijzen.
[2025-01-15 16:31:00] Voorspellen van volgende prijs op tijdstip 14.
[2025-01-15 16:31:00] Actuele prijs: 40000.00 EUR | RSI: 35.00 | Voorspelde prijs: 40500.00 EUR | Voorspelde verandering: 1.25%
[2025-01-15 16:31:00] [SIGNAAL] RSI laag en voorspelde stijging. Tijd om te kopen.
[2025-01-15 16:31:00] [DEMO] Koop 0.01 BTC tegen 40000.00 EUR.
```

---

## Hoe te Gebruiken

1. Maak een `config.json`-bestand met je Bitvavo API-sleutels:
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

2. Stel de gewenste parameters in `trader.json`.

3. Start de bot:
   ```bash
   python trading_bot.py
   ```

4. Controleer de loguitvoer voor signalen en beslissingen.

---

## Opmerking

De bot voert geen echte trades uit als `DEMO_MODE` is ingesteld op `true`. Stel deze parameter in op `false` om live trades uit te voeren.

---

Veel succes met traden! 🚀
