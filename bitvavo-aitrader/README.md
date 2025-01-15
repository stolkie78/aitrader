
# AITRADER Bot - Documentation

## Overview

The AITRADER Bot is a robust tool for medium to long-term trading strategies. It integrates advanced technical indicators like RSI, SMA, and EMA to provide data-driven insights for making profitable trading decisions.

---

## Key Features

1. **Advanced Technical Indicators**:
   - **RSI**: Identifies overbought or oversold conditions.
   - **SMA**: Tracks simple moving averages for trend analysis.
   - **EMA**: Uses exponential moving averages for better response to recent price changes.

2. **Dynamic Thresholds**:
   - Automatically adjusts thresholds based on market volatility, allowing flexible trading strategies.

3. **Daily Reporting**:
   - Logs and calculates daily profit or loss, keeping track of all transactions in `transactions.json`.

4. **Configurable Parameters**:
   - Fully customizable via `config.json` and `trader.json` to adapt to different markets and strategies.

---

## Configuration Files

### `config.json`

This file contains API credentials and general settings:

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

This file allows customization of trading parameters:

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

1. **Configure API Keys and Preferences**:
   - Edit `config.json` with your Bitvavo API credentials.
   - Customize `trader.json` with your desired trading strategy.

2. **Install Dependencies**:
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the Bot**:
   - Start the bot using:
     ```bash
     python trader.py
     ```

4. **Monitor and Analyze**:
   - View real-time logs in the console.
   - Analyze transactions in `transactions.json`.

---

## How It Works

1. **Price Monitoring**:
   - Fetches current prices and tracks historical data.

2. **Technical Analysis**:
   - Uses RSI, SMA, EMA, and dynamic thresholds to make buy/sell decisions.

3. **Transaction Logging**:
   - All transactions are saved in `transactions.json` for historical analysis.

4. **Daily Reporting**:
   - Automatically generates a daily profit/loss report.

---

## Future Enhancements

- Add machine learning models for more accurate predictions.
- Implement notifications for trade alerts.
- Enhance backtesting capabilities to validate strategies.

---

## Disclaimer

This bot is for educational purposes only. Use at your own risk when trading real funds. Always test thoroughly in demo mode first.
