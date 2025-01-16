from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import json
from datetime import datetime, timedelta
from datetime import datetime, timezone
import time

# Configuratie laden


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Configuratiebestanden
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
CHECK_INTERVAL_DAYS = hodl_config["CHECK_INTERVAL_DAYS"]
RSI_OVERBOUGHT = hodl_config["RSI_OVERBOUGHT"]
RSI_OVERSOLD = hodl_config["RSI_OVERSOLD"]
SMA_WINDOW = hodl_config["SMA_WINDOW"]
AI_PREDICTION_WINDOW = hodl_config["AI_PREDICTION_WINDOW"]
DEMO_MODE = hodl_config["DEMO_MODE"]

# Prijsgeschiedenis
price_history = []

# Logfunctie
def log_message(message):
    """Logt een bericht met timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# Historische prijzen ophalen
def get_historical_prices(symbol, days=200):
    """Haal historische prijzen op."""
    end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    candles = bitvavo.candles(
        symbol, '1d', {'start': start_time, 'end': end_time})
    return [float(c[2]) for c in candles]  # Sluitingsprijzen

# Bereken SMA
def calculate_sma(prices, window):
    """Bereken Simple Moving Average."""
    return np.mean(prices[-window:])

# Bereken RSI
def calculate_rsi(prices, window=14):
    """Bereken Relative Strength Index."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)

    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Train AI-model
def train_model(prices):
    """Train een lineair regressiemodel."""
    times = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, prices)
    return model

# Voorspel toekomstige prijs
def predict_price(model, next_time):
    """Voorspel de prijs voor een toekomstig tijdstip."""
    return model.predict([[next_time]])[0][0]

# Plaats een order
def place_order(symbol, side, amount, price):
    """Plaats een order."""
    log_message(f"Placing {side} order: {amount} {symbol} at {price:.2f}")
    try:
        if DEMO_MODE:
            log_message("[DEMO MODE] Geen echte order geplaatst.")
        else:
            order = bitvavo.placeOrder(symbol, side, 'market', {'amount': str(amount)})
            log_message(f"Order geplaatst: {order}")
    except Exception as e:
        log_message(f"Fout bij plaatsen order: {e}")

# Handelslogica
def trading_bot():
    """Lange-termijn HODL-bot met AI-predictie."""
    log_message(f"Start lange-termijn bot voor {SYMBOL}")
    last_trade_date = None

    while True:
        # Controleer alleen 1 keer per CHECK_INTERVAL_DAYS
        if last_trade_date and datetime.now() - last_trade_date < timedelta(days=CHECK_INTERVAL_DAYS):
            log_message("Wachten tot volgende controle.")
            time.sleep(3600)  # Wacht een uur
            continue

        # Haal historische prijzen op
        prices = get_historical_prices(
            SYMBOL, SMA_WINDOW + AI_PREDICTION_WINDOW)
        price_history.extend(prices[-SMA_WINDOW:])
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

        # Beslissingsregels
        if current_price > sma and rsi < RSI_OVERSOLD and price_change > 0:
            log_message("[SIGNAAL] Koopkans gedetecteerd.")
            place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
            last_trade_date = datetime.now()

        elif current_price < sma and rsi > RSI_OVERBOUGHT and price_change < 0:
            log_message("[SIGNAAL] Verkoopkans gedetecteerd.")
            place_order(SYMBOL, 'sell', TRADE_AMOUNT, current_price)
            last_trade_date = datetime.now()

        # Wacht een dag voordat je opnieuw controleert
        time.sleep(24 * 3600)


if __name__ == "__main__":
    trading_bot()
