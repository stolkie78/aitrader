from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import json
import numpy as np
import time
from datetime import datetime

# Laad configuratie vanuit JSON-bestand


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Status en transacties laden/opslaan
STATUS_FILE = "bot_status_scalper.json"
TRANSACTIONS_FILE = "transactions_scalper.json"


def load_status(file_path):
    """Laad de huidige status van de bot."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_action": None, "buy_price": None, "open_position": False}


def save_status(file_path, status):
    """Sla de huidige status van de bot op."""
    with open(file_path, 'w') as f:
        json.dump(status, f)


def load_transactions(file_path):
    """Laad transacties uit een bestand."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_transactions(file_path, transactions):
    """Sla transacties op in een bestand."""
    with open(file_path, 'w') as f:
        json.dump(transactions, f)


# Configuratie laden uit config.json
config = load_config('config.json')

# Bitvavo-instantie aanmaken met configuratie
bitvavo = Bitvavo({
    'APIKEY': config.get('API_KEY'),
    'APISECRET': config.get('API_SECRET'),
    'RESTURL': config.get('RESTURL', 'https://api.bitvavo.com/v2'),
    'WSURL': config.get('WSURL', 'wss://ws.bitvavo.com/v2/'),
    'ACCESSWINDOW': config.get('ACCESSWINDOW', 10000),
    'DEBUGGING': config.get('DEBUGGING', False)
})

# Configuratie laden vanuit trader.json
scalper_config = load_config('scalper.json')
SYMBOL = scalper_config.get("SYMBOL")
THRESHOLD = scalper_config.get("THRESHOLD")
STOP_LOSS = scalper_config.get("STOP_LOSS")
TRADE_AMOUNT = scalper_config.get("TRADE_AMOUNT")
CHECK_INTERVAL = scalper_config.get("CHECK_INTERVAL")
DEMO_MODE = scalper_config.get("DEMO_MODE")
WINDOW_SIZE = scalper_config.get("WINDOW_SIZE", 10)

# Status en transacties laden
status = load_status(STATUS_FILE)
transactions = load_transactions(TRANSACTIONS_FILE)
price_history = []  # Historische prijzen
start_time = datetime.now()  # Starttijd voor dagelijkse rapportage

print(f"Scalping bot gestart met configuratie: {scalper_config}")


def log_message(message):
    """Logt een bericht met timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(f"Fout: Kon de prijs niet ophalen voor {symbol}.")
        raise ValueError(f"Kon de prijs niet ophalen voor {symbol}. Response: {ticker}")
    return float(ticker['price'])


def train_model(prices):
    """Train een lineair regressiemodel."""
    times = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, prices)
    return model


def predict_price(model, next_time):
    """Voorspel de prijs voor de volgende iteratie."""
    return model.predict([[next_time]])[0][0]


def record_transaction(side, amount, price):
    """Registreer een transactie."""
    transaction = {
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': time.time()
    }
    transactions.append(transaction)
    save_transactions(TRANSACTIONS_FILE, transactions)


def generate_daily_report():
    """Genereer een dagelijkse rapportage."""
    total_profit_loss = 0
    for txn in transactions:
        if txn['side'] == 'sell':
            buy_txn = next(
                (t for t in transactions if t['side'] == 'buy' and t['timestamp'] < txn['timestamp']), None)
            if buy_txn:
                profit_loss = (txn['price'] - buy_txn['price']) * txn['amount']
                total_profit_loss += profit_loss

    log_message(f"Dagelijkse winst/verlies: {total_profit_loss:.2f} EUR")
    return total_profit_loss


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie in demo-modus."""
    if DEMO_MODE:
        log_message(f"[DEMO] {side.capitalize()} {amount:.6f} {symbol.split('-')[0]} tegen {price:.2f} EUR.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {
                                    'amount': str(amount)})
            log_message(f"Order geplaatst: {order}")
        except Exception as e:
            log_message(f"Fout bij het plaatsen van de order: {e}")


def trading_bot():
    """Scalping bot met AI-predictie, herstartbare status en dagelijkse rapportage."""
    global status, start_time
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            price_history.append(current_price)

            # Behoud alleen de laatste WINDOW_SIZE prijzen
            if len(price_history) > WINDOW_SIZE:
                price_history.pop(0)

            log_message(f"Huidige prijs van {SYMBOL}: {current_price:.2f} EUR")

            # Alleen trainen als we genoeg data hebben
            if len(price_history) == WINDOW_SIZE:
                model = train_model(price_history)
                next_price = predict_price(model, len(price_history))
                price_change = ((next_price - current_price) /
                                current_price) * 100

                log_message(f"Voorspelde prijs: {next_price:.2f} EUR | Verandering: {price_change:.2f}%")

                if not status["open_position"] and price_change >= THRESHOLD:
                    # Kooppositie openen
                    log_message(f"[INFO] Voorspelling suggereert winst! Koopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR.")
                    place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
                    record_transaction('buy', TRADE_AMOUNT, current_price)
                    status.update(
                        {"last_action": "buy", "buy_price": current_price, "open_position": True})
                    save_status(STATUS_FILE, status)

                elif status["open_position"]:
                    # Controleer stop-loss of take-profit
                    profit_loss = (
                        (current_price - status["buy_price"]) / status["buy_price"]) * 100
                    if profit_loss >= THRESHOLD:
                        log_message(f"[INFO] Take-profit bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR (+{profit_loss:.2f}%).")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        status.update(
                            {"last_action": "sell", "buy_price": None, "open_position": False})
                        save_status(STATUS_FILE, status)
                    elif profit_loss <= STOP_LOSS:
                        log_message(f"[INFO] Stop-loss bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR ({profit_loss:.2f}%).")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        status.update(
                            {"last_action": "sell", "buy_price": None, "open_position": False})
                        save_status(STATUS_FILE, status)

            # Controleer of een nieuwe dag is begonnen
            if (datetime.now() - start_time).days >= 1:
                generate_daily_report()
                start_time = datetime.now()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Trading bot gestopt door gebruiker.")
        generate_daily_report()
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message(f"Scalping bot gestart met herstartbare status voor {SYMBOL}.")
    trading_bot()
