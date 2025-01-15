# Automated Trading Bots Documentation


# Automated Trading Bots Repository

Welcome to the Automated Trading Bots repository! This project contains two powerful trading tools:
1. **Scalper Bot**: A short-term trading bot optimized for scalping strategies.
2. **Trader Bot**: A versatile bot for daily and long-term trading strategies with enhanced configurability.

Both bots leverage AI-driven predictions and technical indicators to assist in making informed trading decisions.

---

## Bots Overview

### **Scalper Bot**
- Designed for quick trades in volatile markets.
- Uses linear regression to predict short-term price movements.
- Features daily profit/loss reporting and restartable functionality.

### **Trader Bot**
- Focuses on medium to long-term trading strategies.
- Utilizes RSI, SMA, and EMA for trend analysis.
- Fully configurable via a JSON file for dynamic adjustments.

---

## Quick Start Guide

1. Clone the repository:
   ```bash
   git clone https://github.com/stolkie78/aitrader.git
   cd trading-bots
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API keys and preferences:
   - Edit `config.json` with your Bitvavo API credentials.
   - Customize `trader.json` or `scalper.json` as needed.

4. Run the desired bot:
   ```bash
   python scalper.py
   # or
   python trader.py
   ```

---

## Disclaimer

These bots are for educational purposes only. Use at your own risk when trading real funds. Always test in demo mode first.

---

## Future Enhancements

- Add backtesting for historical performance analysis.
- Expand technical indicators for enhanced decision-making.
- Implement notification systems for trades and alerts.



---


# Scalper Bot - Documentation

## Overview

The Scalper Bot is a short-term trading tool optimized for quick trades in volatile markets. It leverages AI-driven predictions and daily reporting to ensure a comprehensive trading experience.

---

## Key Features

1. **Daily Reporting**:
   - Calculates and reports daily profit/loss.
   - Stores all transactions in `transactions.json`.

2. **Restartable Status**:
   - The bot saves its state in `bot_status.json` and resumes seamlessly after a restart.

3. **AI-Based Predictions**:
   - Uses linear regression to predict short-term price movements.

---

## Configuration Files

### `config.json`
```json
{
    "API_KEY": "your_api_key",
    "API_SECRET": "your_api_secret",
    "RESTURL": "https://api.bitvavo.com/v2",
    "WSURL": "wss://ws.bitvavo.com/v2/",
    "ACCESSWINDOW": 10000,
    "DEBUGGING": false
}
```

### `scalper.json`
```json
{
    "SYMBOL": "BTC-EUR",
    "WINDOW_SIZE": 10,
    "THRESHOLD": 0.5,
    "STOP_LOSS": -0.7,
    "TRADE_AMOUNT": 0.01,
    "CHECK_INTERVAL": 10,
    "DEMO_MODE": true
}
```

---

## Usage Instructions

1. Configure `config.json` and `scalper.json`.
2. Run the bot:
   ```bash
   python scalper.py
   ```

---

## Disclaimer

This bot is for educational purposes only. Use at your own risk.


---


# Trader Bot - Documentation

## Overview

The Trader Bot is a versatile tool for daily and long-term trading strategies. It features advanced technical indicators and is fully configurable for diverse market conditions.

---

## Key Features

1. **Technical Indicators**:
   - RSI, SMA, and EMA for comprehensive trend analysis.
   - Dynamic thresholds based on market volatility.

2. **Daily Reporting**:
   - Calculates and logs daily profit/loss.

3. **Configurable Parameters**:
   - All trading parameters can be adjusted via `trader.json`.

---

## Configuration Files

### `config.json`
```json
{
    "API_KEY": "your_api_key",
    "API_SECRET": "your_api_secret",
    "RESTURL": "https://api.bitvavo.com/v2",
    "WSURL": "wss://ws.bitvavo.com/v2/",
    "ACCESSWINDOW": 10000,
    "DEBUGGING": false
}
```

### `trader.json`
```json
{
    "SYMBOL": "BTC-EUR",
    "WINDOW_SIZE": 10,
    "THRESHOLD": 2,
    "STOP_LOSS": -1,
    "TRADE_AMOUNT": 0.01,
    "MAX_TOTAL_INVESTMENT": 1000,
    "DEMO_MODE": true,
    "CHECK_INTERVAL": 60,
    "RSI_WINDOW": 14,
    "SMA_WINDOW": 10,
    "EMA_WINDOW": 10,
    "VOLATILITY_MULTIPLIER": 2
}
```

---

## Usage Instructions

1. Configure `config.json` and `trader.json`.
2. Run the bot:
   ```bash
   python trader.py
   ```

---

## Disclaimer

This bot is for educational purposes only. Use at your own risk.
