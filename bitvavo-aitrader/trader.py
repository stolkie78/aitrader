import json
from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import time
from datetime import datetime

# Configuratiebestanden
STATUS_FILE = "trader_status.json"
TRANSACTIONS_FILE = "trader_transactions.json"

# Laad configuratie vanuit JSON-bestand


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Status en transacties laden/opslaan


def load_status(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"open_position": False, "buy_price": None, "last_action": None}


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


# Configuratie laden
config = load_config('config.json')
trader_config = load_config('trader.json')

# Instellen van Bitvavo
bitvavo = Bitvavo({
    'APIKEY': config.get('API_KEY'),
    'APISECRET': config.get('API_SECRET'),
    'RESTURL': config.get('RESTURL', 'https://api.bitvavo.com/v2'),
    'WSURL': config.get('WSURL', 'wss://ws.bitvavo.com/v2/'),
    'ACCESSWINDOW': config.get('ACCESSWINDOW', 10000),
    'DEBUGGING': config.get('DEBUGGING', False)
})

# Variabelen uit configuratie
SYMBOL = trader_config.get("SYMBOL")
WINDOW_SIZE = trader_config.get("WINDOW_SIZE", 10)
THRESHOLD = trader_config.get("THRESHOLD", 2)
STOP_LOSS = trader_config.get("STOP_LOSS", -1)
TRADE_AMOUNT = trader_config.get("TRADE_AMOUNT", 0.01)
MAX_TOTAL_INVESTMENT = trader_config.get("MAX_TOTAL_INVESTMENT", 1000)
DEMO_MODE = trader_config.get("DEMO_MODE", True)
CHECK_INTERVAL = trader_config.get("CHECK_INTERVAL", 60)
RSI_WINDOW = trader_config.get("RSI_WINDOW", 14)
SMA_WINDOW = trader_config.get("SMA_WINDOW", 10)
EMA_WINDOW = trader_config.get("EMA_WINDOW", 10)
VOLATILITY_MULTIPLIER = trader_config.get("VOLATILITY_MULTIPLIER", 2)

# Runtime variabelen
status = load_status(STATUS_FILE)
transactions = load_transactions(TRANSACTIONS_FILE)
price_history = []


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_current_price(symbol):
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(f"Fout: Kon de prijs niet ophalen voor {
                    symbol}. Response: {ticker}")
        raise ValueError(f"Fout bij ophalen van prijs voor {
                        symbol}. Response: {ticker}")
    return float(ticker['price'])

# Technische Indicatoren


def calculate_rsi(prices):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)
    avg_gain = np.mean(gains[-RSI_WINDOW:])
    avg_loss = np.mean(losses[-RSI_WINDOW:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_sma(prices):
    return np.mean(prices[-SMA_WINDOW:])


def calculate_ema(prices):
    weights = np.exp(np.linspace(-1., 0., EMA_WINDOW))
    weights /= weights.sum()
    return np.convolve(prices, weights, mode='valid')[-1]


def calculate_dynamic_threshold(prices):
    volatility = np.std(prices) / np.mean(prices)
    return max(THRESHOLD, VOLATILITY_MULTIPLIER * volatility * 100)

# AI Model: Linear Regression


def train_model(prices):
    times = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, prices)
    return model


def predict_price(model, next_time):
    return model.predict([[next_time]])[0][0]

# Transacties


def record_transaction(side, amount, price):
    transaction = {
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': time.time()
    }
    transactions.append(transaction)
    save_transactions(TRANSACTIONS_FILE, transactions)

# Orders


def place_order(symbol, side, amount, price):
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

# Trading Bot Logic


def trading_bot():
    global status, price_history
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            price_history.append(current_price)

            if len(price_history) > WINDOW_SIZE:
                price_history.pop(0)

            if len(price_history) >= max(RSI_WINDOW, SMA_WINDOW, EMA_WINDOW):
                model = train_model(price_history)
                next_price = predict_price(model, len(price_history))
                price_change = ((next_price - current_price) /
                                current_price) * 100

                sma = calculate_sma(price_history)
                ema = calculate_ema(price_history)
                rsi = calculate_rsi(price_history)
                dynamic_threshold = calculate_dynamic_threshold(price_history)

                log_message(
                    f"Actuele prijs: {current_price:.2f} EUR | SMA: {
                        sma:.2f} | EMA: {ema:.2f} | "
                    f"RSI: {rsi:.2f} | Voorspelde prijs: {
                        next_price:.2f} EUR | "
                    f"Prijsverandering voorspelling: {
                        price_change:.2f}% | Drempel: {dynamic_threshold:.2f}%"
                )

                if not status["open_position"] and current_price > ema and rsi < 70:
                    log_message(f"[INFO] Koopt {TRADE_AMOUNT} {
                                SYMBOL.split('-')[0]}.")
                    place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
                    record_transaction('buy', TRADE_AMOUNT, current_price)
                    status.update(
                        {"open_position": True, "buy_price": current_price, "last_action": "buy"})
                    save_status(STATUS_FILE, status)

                elif status["open_position"]:
                    profit_loss = (
                        (current_price - status["buy_price"]) / status["buy_price"]) * 100
                    if profit_loss >= dynamic_threshold or rsi > 70:
                        log_message(f"[INFO] Verkoopt {TRADE_AMOUNT} {
                                    SYMBOL.split('-')[0]}.")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        status.update(
                            {"open_position": False, "buy_price": None, "last_action": "sell"})
                        save_status(STATUS_FILE, status)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Bot gestopt door gebruiker.")
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message(f"Trading bot gestart voor {SYMBOL}.")
    trading_bot()
