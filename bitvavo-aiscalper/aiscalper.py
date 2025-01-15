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


# Status laden/opslaan
STATUS_FILE = "bot_status.json"


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
config = load_config('trader.json')
SYMBOL = config.get("SYMBOL")
THRESHOLD = config.get("THRESHOLD")
STOP_LOSS = config.get("STOP_LOSS")
TRADE_AMOUNT = config.get("TRADE_AMOUNT")
CHECK_INTERVAL = config.get("CHECK_INTERVAL")
DEMO_MODE = config.get("DEMO_MODE")
WINDOW_SIZE = config.get("WINDOW_SIZE", 10)

# Status laden
status = load_status(STATUS_FILE)
price_history = []  # Historische prijzen

print(f"Trading bot gestart met configuratie: {config}")


def log_message(message):
    """Logt een bericht met timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(f"Fout: Kon de prijs niet ophalen voor {
                    symbol}. Response: {ticker}")
        raise ValueError(f"Kon de prijs niet ophalen voor {
                         symbol}. Response: {ticker}")
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


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie in demo-modus."""
    if DEMO_MODE:
        log_message(f"[DEMO] {side.capitalize()} {amount:.6f} {
                    symbol.split('-')[0]} tegen {price:.2f} EUR.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {
                                       'amount': str(amount)})
            log_message(f"Order geplaatst: {order}")
        except Exception as e:
            log_message(f"Fout bij het plaatsen van de order: {e}")


def trading_bot():
    """Scalping bot met AI-predictie en herstartbare status."""
    global status
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

                log_message(f"Voorspelde prijs: {
                            next_price:.2f} EUR | Verandering: {price_change:.2f}%")

                if not status["open_position"] and price_change >= THRESHOLD:
                    # Take-profit voorspelling - Kooppositie openen
                    log_message(f"[INFO] Voorspelling suggereert winst! Koopt {
                                TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR.")
                    place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
                    status.update(
                        {"last_action": "buy", "buy_price": current_price, "open_position": True})
                    save_status(STATUS_FILE, status)

                elif status["open_position"]:
                    # Controleer stop-loss of take-profit bij open positie
                    profit_loss = (
                        (current_price - status["buy_price"]) / status["buy_price"]) * 100
                    if profit_loss >= THRESHOLD:
                        log_message(f"[INFO] Take-profit bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {
                                    current_price:.2f} EUR (+{profit_loss:.2f}%).")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        status.update(
                            {"last_action": "sell", "buy_price": None, "open_position": False})
                        save_status(STATUS_FILE, status)
                    elif profit_loss <= STOP_LOSS:
                        log_message(f"[INFO] Stop-loss bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {
                                    current_price:.2f} EUR ({profit_loss:.2f}%).")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        status.update(
                            {"last_action": "sell", "buy_price": None, "open_position": False})
                        save_status(STATUS_FILE, status)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Trading bot gestopt door gebruiker.")
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message("Scalping bot gestart met herstartbare status.")
    trading_bot()
