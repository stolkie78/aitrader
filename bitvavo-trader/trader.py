import json
from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import time
from datetime import datetime

# Configuratiebestanden
STATUS_FILE = "bot_status.json"
TRANSACTIONS_FILE = "transactions.json"

# Configuratie laden


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def load_status(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"open_position": False, "last_action": None, "buy_price": None}


def save_status(file_path, status):
    with open(file_path, 'w') as f:
        json.dump(status, f)


def load_transactions(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_transactions(file_path, transactions):
    with open(file_path, 'w') as f:
        json.dump(transactions, f)


config = load_config('config.json')
trader_config = load_config('trader.json')

# Bitvavo-instantie instellen
bitvavo = Bitvavo({
    'APIKEY': config.get('API_KEY'),
    'APISECRET': config.get('API_SECRET'),
    'RESTURL': config.get('RESTURL', 'https://api.bitvavo.com/v2'),
    'WSURL': config.get('WSURL', 'wss://ws.bitvavo.com/v2/'),
    'ACCESSWINDOW': config.get('ACCESSWINDOW', 10000),
    'DEBUGGING': config.get('DEBUGGING', False)
})

# Configuratievariabelen
SYMBOL = trader_config.get("SYMBOL")
WINDOW_SIZE = trader_config.get("WINDOW_SIZE", 14)
THRESHOLD = trader_config.get("THRESHOLD", 0.5)
TRADE_AMOUNT = trader_config.get("TRADE_AMOUNT", 0.01)
RSI_OVERBOUGHT = trader_config.get("RSI_OVERBOUGHT", 70)
RSI_OVERSOLD = trader_config.get("RSI_OVERSOLD", 30)
DEMO_MODE = trader_config.get("DEMO_MODE", True)
CHECK_INTERVAL = trader_config.get("CHECK_INTERVAL", 60)

# Prijsgeschiedenis, status en transacties
price_history = []
status = load_status(STATUS_FILE)
transactions = load_transactions(TRANSACTIONS_FILE)

# Logfunctie


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# Actuele prijs ophalen


def get_current_price(symbol):
    log_message(f"Ophalen van actuele prijs voor {symbol}.")
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(f"Fout: Geen prijsinformatie beschikbaar voor {symbol}.")
        raise ValueError(
            f"Fout bij ophalen prijs {symbol}. Response: {ticker}")
    price = float(ticker['price'])
    log_message(f"Actuele prijs voor {symbol}: {price:.2f} EUR.")
    return price

# Bereken RSI


def calculate_rsi(prices):
    log_message("Berekenen van RSI.")
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)

    avg_gain = np.mean(gains[-WINDOW_SIZE:])
    avg_loss = np.mean(losses[-WINDOW_SIZE:])
    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    log_message(f"Berekenende RSI: {rsi:.2f}")
    return rsi

# AI-predictie (Lineaire Regressie)


def train_model(prices):
    log_message("AI-model trainen met historische prijzen.")
    times = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, prices)
    log_message("AI-model succesvol getraind.")
    return model


def predict_price(model, next_time):
    log_message(f"Voorspellen van volgende prijs op tijdstip {next_time}.")
    predicted_price = model.predict([[next_time]])[0][0]
    log_message(f"Voorspelde prijs: {predicted_price:.2f} EUR.")
    return predicted_price

# Handelslogica


def record_transaction(side, amount, price):
    transaction = {
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': datetime.now().isoformat()
    }
    transactions.append(transaction)
    save_transactions(TRANSACTIONS_FILE, transactions)
    log_message(f"Transactie geregistreerd: {transaction}.")


def trading_bot():
    global price_history, status
    try:
        log_message(f"Trading bot gestart voor {SYMBOL}.")
        while True:
            current_price = get_current_price(SYMBOL)
            price_history.append(current_price)

            # Behoud alleen de laatste WINDOW_SIZE prijzen
            if len(price_history) > WINDOW_SIZE:
                price_history.pop(0)

            if len(price_history) == WINDOW_SIZE:
                rsi = calculate_rsi(price_history)
                model = train_model(price_history)
                next_price = predict_price(model, len(price_history))
                price_change = ((next_price - current_price) /
                                current_price) * 100

                log_message(
                    f"Actuele prijs: {current_price:.2f} EUR | RSI: {rsi:.2f} | "
                    f"Voorspelde prijs: {next_price:.2f} EUR | "
                    f"Voorspelde verandering: {price_change:.2f}%"
                )

                # Koopactie
                if not status["open_position"] and rsi < RSI_OVERSOLD and price_change > THRESHOLD:
                    log_message(
                        "[SIGNAAL] RSI laag en voorspelde stijging. Tijd om te kopen.")
                    if DEMO_MODE:
                        log_message(
                            f"[DEMO] Koop {TRADE_AMOUNT} {SYMBOL.split('-')[0]} tegen {current_price:.2f} EUR.")
                    else:
                        record_transaction('buy', TRADE_AMOUNT, current_price)
                        status.update(
                            {"open_position": True, "buy_price": current_price})
                        save_status(STATUS_FILE, status)

                # Verkoopactie
                elif status["open_position"] and (rsi > RSI_OVERBOUGHT or price_change < -THRESHOLD):
                    log_message(
                        "[SIGNAAL] RSI hoog of voorspelde daling. Tijd om te verkopen.")
                    if DEMO_MODE:
                        log_message(
                            f"[DEMO] Verkoop {TRADE_AMOUNT} {SYMBOL.split('-')[0]} tegen {current_price:.2f} EUR.")
                    else:
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        status.update(
                            {"open_position": False, "buy_price": None})
                        save_status(STATUS_FILE, status)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Bot gestopt door gebruiker.")
    except Exception as e:
        log_message(f"Fout: {e}")


if __name__ == "__main__":
    trading_bot()
