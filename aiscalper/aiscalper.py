from python_bitvavo_api.bitvavo import Bitvavo
import json
import time
from datetime import datetime

# Laad configuratie vanuit JSON-bestand
def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

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
# Gebruik de waardes uit de trader.json
SYMBOL = config.get("SYMBOL")
THRESHOLD = config.get("THRESHOLD")
STOP_LOSS = config.get("STOP_LOSS")
TRADE_AMOUNT = config.get("TRADE_AMOUNT")
CHECK_INTERVAL = config.get("CHECK_INTERVAL")
DEMO_MODE = config.get("DEMO_MODE")

print(f"Trading bot gestart met configuratie: {config}")

def log_message(message):
    """Logt een bericht met timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(
            f"Fout: Kon de prijs niet ophalen voor {symbol}. Response: {ticker}")
        raise ValueError(
            f"Kon de prijs niet ophalen voor {symbol}. Response: {ticker}")
    return float(ticker['price'])


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie in demo-modus."""
    if DEMO_MODE:
        log_message(
            f"[DEMO] {side.capitalize()} {amount:.6f} {symbol.split('-')[0]} tegen {price:.2f} EUR.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {
                                    'amount': str(amount)})
            log_message(f"Order geplaatst: {order}")
        except Exception as e:
            log_message(f"Fout bij het plaatsen van de order: {e}")


def trading_bot():
    """Scalping bot voor daytrading met meer logging."""
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            log_message(f"Huidige prijs van {SYMBOL}: {current_price:.2f} EUR")

            # Simuleer een kooppositie
            buy_price = current_price
            log_message(
                f"[INFO] Koopt {TRADE_AMOUNT} BTC tegen {buy_price:.2f} EUR.")
            place_order(SYMBOL, 'buy', TRADE_AMOUNT, buy_price)

            # Monitor de positie
            while True:
                current_price = get_current_price(SYMBOL)
                price_change = ((current_price - buy_price) / buy_price) * 100
                log_message(
                    f"Actuele prijs: {current_price:.2f} EUR | Verandering: {price_change:.2f}%")

                if price_change >= THRESHOLD:
                    # Take-profit
                    log_message(
                        f"[INFO] Take-profit bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR (+{price_change:.2f}%).")
                    place_order(SYMBOL, 'sell', TRADE_AMOUNT, current_price)
                    break

                elif price_change <= STOP_LOSS:
                    # Stop-loss
                    log_message(
                        f"[INFO] Stop-loss bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR ({price_change:.2f}%).")
                    place_order(SYMBOL, 'sell', TRADE_AMOUNT, current_price)
                    break

                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("Trading bot gestopt door gebruiker.")
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message("Scalping bot gestart.")
    trading_bot()
