import json
from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import time
from datetime import datetime

# Laad configuratie vanuit JSON-bestand


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Configuratie laden
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
trader_config = load_config('trader.json')

# Instellen van munt en parameters
SYMBOL = trader_config.get("SYMBOL")
WINDOW_SIZE = trader_config.get("WINDOW_SIZE", 10)
THRESHOLD = trader_config.get("THRESHOLD", 2)
STOP_LOSS = trader_config.get("STOP_LOSS", -1)
TRADE_AMOUNT = trader_config.get("TRADE_AMOUNT", 0.01)
MAX_TOTAL_INVESTMENT = trader_config.get("MAX_TOTAL_INVESTMENT", 1000)
DEMO_MODE = trader_config.get("DEMO_MODE", True)
CHECK_INTERVAL = trader_config.get("CHECK_INTERVAL", 60)

# Variabelen voor runtime
price_history = []
transactions = []
current_investment = 0
buy_price = None
open_position = False


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


def calculate_rsi(prices, window=14):
    """Bereken de Relative Strength Index (RSI)."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, abs(deltas), 0)

    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_sma(prices, window):
    """Bereken Simple Moving Average (SMA)."""
    return np.mean(prices[-window:])


def calculate_ema(prices, window):
    """Bereken Exponential Moving Average (EMA)."""
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    return np.convolve(prices, weights, mode='valid')[-1]


def calculate_dynamic_threshold(prices):
    """Bereken een dynamische drempel op basis van volatiliteit."""
    volatility = np.std(prices) / np.mean(prices)
    return max(1.5, 2 * volatility * 100)  # Minimum van 1.5%


def record_transaction(side, amount, price):
    """Registreer een transactie."""
    transactions.append({
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': time.time()
    })


def generate_report():
    """Genereer een dagelijkse rapportage van winst/verlies."""
    total_profit_loss = 0
    for txn in transactions:
        if txn['side'] == 'sell':
            buy_txn = next(
                (t for t in transactions if t['side'] == 'buy' and t['timestamp'] < txn['timestamp']), None)
            if buy_txn:
                profit_loss = (txn['price'] - buy_txn['price']) * txn['amount']
                total_profit_loss += profit_loss
    log_message(f"Totale winst/verlies: {total_profit_loss:.2f} EUR")
    return total_profit_loss


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
    """Trading bot met verbeterde voorspellingen en rapportage."""
    global price_history, open_position, buy_price, current_investment
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            price_history.append(current_price)

            # Behoud alleen de laatste WINDOW_SIZE prijzen
            if len(price_history) > WINDOW_SIZE:
                price_history.pop(0)

            log_message(f"Huidige prijs van {SYMBOL}: {current_price:.2f} EUR")

            # Analyseer trends als er genoeg data is
            if len(price_history) >= WINDOW_SIZE:
                sma = calculate_sma(price_history, WINDOW_SIZE)
                ema = calculate_ema(price_history, WINDOW_SIZE)
                rsi = calculate_rsi(price_history)

                log_message(f"SMA: {sma:.2f}, EMA: {ema:.2f}, RSI: {rsi:.2f}")

                threshold = calculate_dynamic_threshold(price_history)

                if not open_position and current_price > ema and rsi < 70:
                    # Open een kooppositie
                    log_message(f"[INFO] Trendanalyse suggereert winst. Koopt {
                                TRADE_AMOUNT} {SYMBOL.split('-')[0]}.")
                    place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
                    record_transaction('buy', TRADE_AMOUNT, current_price)
                    buy_price = current_price
                    open_position = True
                    current_investment += TRADE_AMOUNT * current_price

                elif open_position:
                    profit_loss = (
                        (current_price - buy_price) / buy_price) * 100
                    if profit_loss >= threshold or rsi > 70:
                        log_message(
                            f"[INFO] Take-profit bereikt. Verkoopt {TRADE_AMOUNT} {SYMBOL.split('-')[0]}.")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        open_position = False
                        buy_price = None
                        current_investment -= TRADE_AMOUNT * current_price

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Trading bot gestopt door gebruiker.")
        generate_report()
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message(f"Trading bot gestart voor {SYMBOL}.")
    trading_bot()
