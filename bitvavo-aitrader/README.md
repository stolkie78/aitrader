
# Updated Trader Bot Documentation

## Overview

This updated trader bot incorporates advanced features for long-term success, including:

1. **Technical Indicators**: RSI, SMA, and EMA for better trend analysis.
2. **Dynamic Thresholds**: Adjusts thresholds based on market volatility.
3. **Data Analysis and Reporting**: Tracks and reports daily profit/loss.
4. **Trend Analysis**: Uses SMA and EMA to detect trends effectively.

---

## Technical Indicators

### RSI (Relative Strength Index)

- Indicates whether a market is overbought (>70) or oversold (<30).
- Helps refine buy/sell decisions.

### SMA (Simple Moving Average)

- Calculates the average price over a given window.

### EMA (Exponential Moving Average)

- Gives more weight to recent prices for detecting recent trends.

---

## Key Features

1. **RSI**: Identifies overbought/oversold conditions.
2. **SMA/EMA**: Tracks moving averages for trend detection.
3. **Dynamic Thresholds**: Adapts to market volatility.
4. **Daily Reporting**: Logs transactions and calculates profit/loss.

---

## Example Configuration Files

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
    "WINDOW_SIZE": 20,
    "THRESHOLD": 3,
    "STOP_LOSS": -2,
    "TRADE_AMOUNT": 0.01,
    "MAX_TOTAL_INVESTMENT": 5000,
    "DEMO_MODE": true,
    "CHECK_INTERVAL": 3600
}
```

---

## How to Use

1. **Setup `config.json`**:
   - Add your Bitvavo API keys and preferences.

2. **Setup `trader.json`**:
   - Define the trading parameters, such as `SYMBOL`, `THRESHOLD`, and `CHECK_INTERVAL`.

3. **Run the bot**:
   - Execute the script to start trading.

---

## Future Improvements

1. Backtesting to analyze performance.
2. Integration with additional technical indicators.
3. Automated alerts for key events.

---

## Disclaimer

This script is for educational purposes only. Use at your own risk when trading real funds.
