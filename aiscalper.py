from python_bitvavo_api.bitvavo import Bitvavo
import time
from datetime import datetime

# Configureer je API-sleutels hier
API_KEY = 'jouw_api_key'
API_SECRET = 'jouw_api_secret'

# Instantie van Bitvavo API
bitvavo = Bitvavo({
    'APIKEY': API_KEY,
    'APISECRET': API_SECRET,
    'RESTURL': 'https://api.bitvavo.com/v2',
    'WSURL': 'wss://ws.bitvavo.com/v2/',
    'ACCESSWINDOW': 10000,
    'DEBUGGING': False
})

# Configuratie
SYMBOL = 'BTC-EUR'  # Trading paar
THRESHOLD = 0.5  # Percentage winst voor take-profit
STOP_LOSS = -0.7  # Percentage verlies om te stoppen
TRADE_AMOUNT = 0.005  # Hoeveelheid BTC per trade
CHECK_INTERVAL = 10  # Interval in seconden tussen prijschecks
DEMO_MODE = False  # Zet op False om echte trades uit te voeren


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        raise ValueError(
            f"Kon de prijs niet ophalen voor {symbol}. Response: {ticker}")
    return float(ticker['price'])


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie in demo-modus."""
    if DEMO_MODE:
        print(
            f"[DEMO] {side.capitalize()} {amount:.6f} {symbol.split('-')[0]} tegen {price:.2f} EUR.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {
                                       'amount': str(amount)})
            print(f"Order geplaatst: {order}")
        except Exception as e:
            print(f"Fout bij het plaatsen van de order: {e}")


def trading_bot():
    """Scalping bot voor daytrading."""
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Huidige prijs: {current_price:.2f} EUR")

            # Simuleer een kooppositie
            buy_price = current_price
            print(
                f"[INFO] Koopt {TRADE_AMOUNT} BTC tegen {buy_price:.2f} EUR.")
            place_order(SYMBOL, 'buy', TRADE_AMOUNT, buy_price)

            # Monitor de positie
            while True:
                current_price = get_current_price(SYMBOL)
                price_change = ((current_price - buy_price) / buy_price) * 100

                if price_change >= THRESHOLD:
                    # Take-profit
                    print(
                        f"[INFO] Take-profit bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR (+{price_change:.2f}%).")
                    place_order(SYMBOL, 'sell', TRADE_AMOUNT, current_price)
                    break

                elif price_change <= STOP_LOSS:
                    # Stop-loss
                    print(
                        f"[INFO] Stop-loss bereikt! Verkoopt {TRADE_AMOUNT} BTC tegen {current_price:.2f} EUR ({price_change:.2f}%).")
                    place_order(SYMBOL, 'sell', TRADE_AMOUNT, current_price)
                    break

                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("Trading bot gestopt.")
    except Exception as e:
        print(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    print("Scalping bot gestart.")
    trading_bot()
