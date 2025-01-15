
# Scalper Bot - Version 0.1

## Overview

The **Scalper Bot** is a powerful trading tool designed for short-term trading strategies. It uses AI-driven predictions, detailed transaction tracking, and restartable functionality to provide a robust and reliable trading experience.

---

## Key Features

1. **Daily Reporting**
   - Automatically calculates and reports daily profit/loss.
   - Saves all transactions in a `transactions.json` file for historical analysis.

2. **Restartable Status**
   - The bot saves its current state in `bot_status.json`.
   - Open positions and the last action are restored upon restart.

3. **AI-Based Predictions**
   - Uses linear regression to predict price movements based on a configurable window (`WINDOW_SIZE`).

4. **Flexible Configuration**
   - Configurable via `config.json` and `trader.json` for easy adaptation to different trading strategies.

5. **Demo Mode**
   - Allows users to simulate trading without executing real trades, enabling safe testing of strategies.

---

## Configuration Files

### `config.json`

This file contains API keys and general bot settings:

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

This file specifies trading parameters:

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

## How It Works

1. **Price Monitoring**:
   - The bot fetches current prices and tracks historical price data.

2. **Prediction and Decision Making**:
   - It predicts future prices using linear regression and decides to buy or sell based on configured thresholds.

3. **Transaction Tracking**:
   - Each transaction is logged in `transactions.json`, preserving a complete trade history.

4. **Daily Reports**:
   - At the end of each day, the bot generates a report of daily profit or loss.

---

## Usage Instructions

1. **Setup Configuration Files**:
   - Edit `config.json` with your Bitvavo API credentials.
   - Adjust `trader.json` to fit your trading strategy.

2. **Run the Bot**:
   - Start the bot using Python:  
     ```bash
     python scalper.py
     ```

3. **Monitor Logs**:
   - View real-time logs in the console for updates and actions taken by the bot.

4. **Check Reports**:
   - View daily reports of profit/loss in the console or analyze the `transactions.json` file for detailed transaction history.

---

## Limitations

- The bot relies on linear regression, which may not always account for sudden market changes.
- For real trading, ensure thresholds and stop-loss values align with your risk tolerance.

---

## Future Improvements

1. **Backtesting**:
   - Simulate past performance using historical data.

2. **Additional Indicators**:
   - Integrate more technical indicators like RSI or MACD.

3. **Enhanced Reporting**:
   - Provide more detailed analytics and visualization of trade performance.

---

## Disclaimer

This bot is for educational purposes only. Use at your own risk. Always test in demo mode before engaging in real trading.
