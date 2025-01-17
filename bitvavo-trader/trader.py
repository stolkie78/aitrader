import time
import json
from datetime import datetime
from python_bitvavo_api.bitvavo import Bitvavo
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# Configuratie laden


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Slack-bericht sturen


def send_to_slack(message, webhook_url):
    payload = {"text": message}
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"[ERROR] Kon bericht niet naar Slack sturen: {e}")

# Logging


def log_message(message, webhook_url=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = f"[TARGET BOT] {timestamp} - {message}"
    print(log)
    if webhook_url:
        send_to_slack(log, webhook_url)

# Technische indicatoren berekenen


def calculate_indicators(prices, trader_config):
    slow_macd = trader_config["slow_macd"]
    fast_macd = trader_config["fast_macd"]
    signal_macd = trader_config["signal_macd"]
    sma_period = trader_config["sma_period"]
    ema_period = trader_config["ema_period"]

    df = pd.DataFrame(prices, columns=["price"])
    df["sma"] = df["price"].rolling(window=sma_period).mean()
    df["ema"] = df["price"].ewm(span=ema_period, adjust=False).mean()
    df["rsi"] = calculate_rsi(df["price"])
    df["macd"], df["macd_signal"] = calculate_macd(
        df["price"], slow_macd, fast_macd, signal_macd)
    return df


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(prices, slow=26, fast=12, signal=9):
    fast_ema = prices.ewm(span=fast, adjust=False).mean()
    slow_ema = prices.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

# AI-model trainen


def train_ai_model(data):
    features = data[["price_change", "rsi", "macd", "macd_signal"]].dropna()
    targets = data["future_price_change"].dropna()
    model = LinearRegression()
    model.fit(features, targets)
    return model

# Bot met AI, indicatoren, winstdoel en stop-loss


def midterm_bot(config_file, trader_file):
    # Configuratie laden
    config = load_config(config_file)
    trader_config = load_config(trader_file)

    symbol = trader_config["symbol"]
    initial_budget = trader_config["initial_budget"]
    target_profit_percent = trader_config["target_profit_percent"]
    stop_loss_percent = trader_config["stop_loss_percent"]
    check_interval = trader_config["check_interval"]
    rsi_threshold_buy = trader_config["rsi_threshold_buy"]
    rsi_threshold_sell = trader_config["rsi_threshold_sell"]
    prediction_threshold_buy = trader_config["prediction_threshold_buy"]

    bitvavo = Bitvavo({
        "APIKEY": config.get("API_KEY"),
        "APISECRET": config.get("API_SECRET"),
        "RESTURL": config.get("RESTURL", "https://api.bitvavo.com/v2"),
        "WSURL": config.get("WSURL", "wss://ws.bitvavo.com/v2/"),
        "ACCESSWINDOW": config.get("ACCESSWINDOW", 10000),
        "DEBUGGING": config.get("DEBUGGING", False),
    })
    slack_webhook_url = config.get("SLACK_WEBHOOK_URL")

    prices = pd.Series(dtype=float)
    model = None
    bought = False
    buy_price = 0
    amount_crypto = 0

    log_message(
        f"Bot gestart voor {symbol}. Budget: {initial_budget:.2f} EUR, Doelwinst: {target_profit_percent}%, Stop-loss: {stop_loss_percent}%.", slack_webhook_url)

    try:
        while True:
            # Huidige prijs ophalen
            ticker = bitvavo.tickerPrice({"market": symbol})
            current_price = float(ticker["price"])
            prices = prices.append(
                pd.Series([current_price]), ignore_index=True)

            # Indicatoren en AI-model
            if len(prices) > 50:
                prices = prices[-50:]  # Behoud de laatste 50 prijzen
                indicators = calculate_indicators(prices, trader_config)
                indicators["price_change"] = prices.pct_change()
                indicators["future_price_change"] = indicators["price_change"].shift(
                    -1)
                model = train_ai_model(indicators.dropna())

                # Koopactie
                if not bought:
                    prediction = model.predict(
                        indicators[["price_change", "rsi", "macd", "macd_signal"]].iloc[-1:].values)[0]
                    rsi = indicators["rsi"].iloc[-1]
                    if prediction <= prediction_threshold_buy and rsi < rsi_threshold_buy:  # Oversold en voorspelling negatief
                        amount_crypto = initial_budget / current_price
                        place_order(bitvavo, symbol, "buy", amount_crypto)
                        buy_price = current_price
                        bought = True
                        log_message(
                            f"[INFO] Gekocht {amount_crypto:.6f} {symbol.split('-')[0]} tegen {buy_price:.2f} EUR.", slack_webhook_url)

                # Verkoopactie
                if bought:
                    current_value = amount_crypto * current_price
                    profit_percent = (
                        (current_value - initial_budget) / initial_budget) * 100

                    if profit_percent >= target_profit_percent:  # Doelwinst bereikt
                        place_order(bitvavo, symbol, "sell", amount_crypto)
                        log_message(
                            f"[INFO] Doelwinst bereikt! Verkocht voor {current_value:.2f} EUR. Winst: {profit_percent:.2f}%.", slack_webhook_url)
                        break

                    if profit_percent <= stop_loss_percent:  # Stop-loss bereikt
                        place_order(bitvavo, symbol, "sell", amount_crypto)
                        log_message(
                            f"[INFO] Stop-loss geactiveerd. Verkocht voor {current_value:.2f} EUR. Verlies: {profit_percent:.2f}%.", slack_webhook_url)
                        break

            time.sleep(check_interval)

    except KeyboardInterrupt:
        log_message("Bot gestopt door gebruiker.", slack_webhook_url)
    except Exception as e:
        log_message(f"[ERROR] Fout in bot: {e}", slack_webhook_url)


if __name__ == "__main__":
    midterm_bot("config.json", "trader.json")
