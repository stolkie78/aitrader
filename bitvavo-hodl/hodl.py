from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import json
import requests
from datetime import datetime, timedelta, timezone
import os
import time

# Configuratiebestanden
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Configuratie laden
config = load_config("config.json")
hodl_config = load_config("hodl.json")

# Bitvavo-instantie
bitvavo = Bitvavo({
    'APIKEY': config['API_KEY'],
    'APISECRET': config['API_SECRET'],
    'RESTURL': 'https://api.bitvavo.com/v2',
    'WSURL': 'wss://ws.bitvavo.com/v2/',
    'ACCESSWINDOW': 10000,
    'DEBUGGING': False
})

# Configuratievariabelen
SYMBOL = hodl_config["SYMBOL"]
TRADE_AMOUNT = hodl_config["TRADE_AMOUNT"]
CHECK_INTERVAL = hodl_config["CHECK_INTERVAL"]
RSI_OVERBOUGHT = hodl_config["RSI_OVERBOUGHT"]
RSI_OVERSOLD = hodl_config["RSI_OVERSOLD"]
SMA_WINDOW = hodl_config["SMA_WINDOW"]
AI_PREDICTION_WINDOW = hodl_config["AI_PREDICTION_WINDOW"]
DEMO_MODE = hodl_config["DEMO_MODE"]

# Configuratie laden uit slack.json
slack_config = load_config('slack.json')
SLACK_WEBHOOK_URL = slack_config.get("SLACK_WEBHOOK_URL")
print(f"Slack configuratie: {slack_config}")

# Dynamische bestandsnamen
STATUS_FILE = os.path.join(DATA_DIR, f"status_{SYMBOL}.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, f"transactions_{SYMBOL}.json")

# Laad en sla status op
def load_status(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"open_position": False, "last_action": None, "buy_price": None}


def save_status(file_path, status):
    with open(file_path, 'w') as f:
        json.dump(status, f, indent=4)

# Laad en sla transacties op
def load_transactions(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_transactions(file_path, transactions):
    with open(file_path, 'w') as f:
        json.dump(transactions, f, indent=4)


print(f"HODL bot gestart met configuratie: {hodl_config}")

# Slack-bericht sturen
def send_to_slack(message):
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[FOUT] Kon bericht niet naar Slack sturen: {e}")


# Logfunctie
def log_message(message):
    if DEMO_MODE:
        RUNSTATUS = "[DEMO]"
    else:
        RUNSTATUS = "[PROD]"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{RUNSTATUS}[HODL][{SYMBOL}][{timestamp}] {message}")
    send_to_slack(f"{RUNSTATUS}[HODL][{SYMBOL}] {message}")

# Historische prijzen ophalen
def get_historical_prices(symbol, days=200):
    end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    candles = bitvavo.candles(
        symbol, '1d', {'start': start_time, 'end': end_time})
    return [float(c[2]) for c in candles]  # Sluitingsprijzen

# Bereken SMA
def calculate_sma(prices, window):
    return np.mean(prices[-window:])

# Bereken RSI
def calculate_rsi(prices, window=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)

    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# AI-modellering
def train_model(prices):
    times = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, prices)
    return model


def predict_price(model, next_time):
    return model.predict([[next_time]])[0][0]

# Plaats order
def place_order(symbol, side, amount, price, transactions):
    log_message(f"Placing {side} order: {amount} {symbol} at {price:.2f}")
    transaction = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "side": side,
        "amount": amount,
        "price": price
    }
    transactions.append(transaction)
    save_transactions(TRANSACTIONS_FILE, transactions)

    if DEMO_MODE:
        log_message("[DEMO MODE] Geen echte order geplaatst.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {'amount': str(amount)})
            log_message(f"Order geplaatst: {order}")
        except Exception as e:
            log_message(f"Fout bij plaatsen order: {e}")

# Rapportage


def generate_report(transactions):
    total_profit_loss = 0
    for txn in transactions:
        if txn['side'] == 'sell':
            buy_txn = next(
                (t for t in transactions if t['side'] == 'buy' and t['timestamp'] < txn['timestamp']),
                None
            )
            if buy_txn:
                profit_loss = (txn['price'] - buy_txn['price']) * txn['amount']
                total_profit_loss += profit_loss

    log_message(f"Totale winst/verlies: {total_profit_loss:.2f} EUR")
    log_message("Transacties:")
    for txn in transactions:
        log_message(f"{txn['timestamp']} | {txn['side'].capitalize()} | "
                    f"Hoeveelheid: {txn['amount']:.6f}, Prijs: {txn['price']:.2f}")

# Handelslogica
def trading_bot():
    log_message(f"Start HODL-strategie bot voor {SYMBOL}")
    last_trade_date = None
    status = load_status(STATUS_FILE)
    transactions = load_transactions(TRANSACTIONS_FILE)

    while True:
        # Controleer alleen 1 keer per CHECK_INTERVAL_DAYS
        if last_trade_date and datetime.now() - last_trade_date < timedelta(days=CHECK_INTERVAL_DAYS):
            log_message("Wachten tot volgende controle.")
            time.sleep(3600)
            continue

        # Haal historische prijzen op
        prices = get_historical_prices(
            SYMBOL, SMA_WINDOW + AI_PREDICTION_WINDOW)
        current_price = prices[-1]

        # Indicatorberekeningen
        sma = calculate_sma(prices, SMA_WINDOW)
        rsi = calculate_rsi(prices, 14)

        # AI-predictie
        model = train_model(prices[-AI_PREDICTION_WINDOW:])
        next_price = predict_price(model, len(prices))
        price_change = ((next_price - current_price) / current_price) * 100

        log_message(
            f"Huidige prijs: {current_price:.2f}, SMA: {sma:.2f}, RSI: {rsi:.2f}, "
            f"Voorspelde prijs: {next_price:.2f}, Voorspelde verandering: {price_change:.2f}%"
        )

        # Koop-/Verkooplogica
        if current_price > sma and rsi < RSI_OVERSOLD and price_change > 0:
            log_message("[SIGNAAL] Koopkans gedetecteerd.")
            place_order(SYMBOL, 'buy', TRADE_AMOUNT,
                        current_price, transactions)
            status.update(
                {"open_position": True, "buy_price": current_price, "last_action": "buy"})
            save_status(STATUS_FILE, status)
            last_trade_date = datetime.now()

        elif current_price < sma and rsi > RSI_OVERBOUGHT and price_change < 0:
            log_message("[SIGNAAL] Verkoopkans gedetecteerd.")
            place_order(SYMBOL, 'sell', TRADE_AMOUNT,
                        current_price, transactions)
            status.update(
                {"open_position": False, "buy_price": None, "last_action": "sell"})
            save_status(STATUS_FILE, status)
            last_trade_date = datetime.now()

        # Rapportage
        generate_report(transactions)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    trading_bot()
