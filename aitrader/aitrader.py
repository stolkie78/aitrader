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

# Toewijzen van variabelen uit de configuratie
SYMBOLS = config.get("SYMBOLS", [])
WINDOW_SIZE = config.get("WINDOW_SIZE", 10)
THRESHOLD = config.get("THRESHOLD", 2)
MAX_TOTAL_INVESTMENT = config.get("MAX_TOTAL_INVESTMENT", 1000)
current_investment = config.get("current_investment", 0)
DAILY_DATA = config.get("DAILY_DATA", {})
START_TIME = time.time()
DEMO_MODE = config.get("DEMO_MODE", True)
SLEEP_INTERVAL = config.get("SLEEP_INTERVAL", 3600)

print(f"Trading bot gestart met configuratie: {config}")


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        raise ValueError(
            f"Kon de prijs niet ophalen voor {symbol}. Response: {ticker}")
    return float(ticker['price'])


def train_model(prices):
    """Train een lineair regressiemodel."""
    data = np.array(prices).reshape(-1, 1)
    times = np.arange(len(data)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, data)
    return model


def predict_price(model, next_time):
    """Voorspel de volgende prijs."""
    return model.predict([[next_time]])[0][0]


def record_transaction(symbol, side, amount, price):
    """Registreer een transactie."""
    DAILY_DATA[symbol]['transactions'].append({
        'side': side,
        'amount': amount,
        'price': price,
        'timestamp': time.time()
    })


def calculate_daily_profit_loss(symbol):
    """Bereken de dagelijkse winst/verlies voor een specifieke munt."""
    transactions = DAILY_DATA[symbol]['transactions']
    if not transactions:
        return 0

    profit_loss = 0
    for txn in transactions:
        if txn['side'] == 'sell':
            buy_txns = [t for t in transactions if t['side']
                        == 'buy' and t['timestamp'] < txn['timestamp']]
            if buy_txns:
                avg_buy_price = sum(t['price']
                                    for t in buy_txns) / len(buy_txns)
                profit_loss += (txn['price'] - avg_buy_price) * txn['amount']
    return profit_loss


def daily_report():
    """Toon een dagelijkse winst/verlies rapportage."""
    print("\n--- Dagelijkse Winst/Verlies Rapport ---")
    for symbol in SYMBOLS:
        profit_loss = calculate_daily_profit_loss(symbol)
        print(f"{symbol}: Winst/Verlies: {profit_loss:.2f} EUR")
    print("----------------------------------------\n")


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie van de order in demo-modus."""
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
    """Trading bot met meer informatie tijdens de run."""
    global current_investment, START_TIME

    try:
        while True:
            print(
                f"\n--- Nieuwe Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            for symbol in SYMBOLS:
                current_price = get_current_price(symbol)
                print(f"Huidige prijs van {symbol}: {current_price:.2f} EUR")
                DAILY_DATA[symbol]['prices'].append(current_price)

                if len(DAILY_DATA[symbol]['prices']) > WINDOW_SIZE:
                    DAILY_DATA[symbol]['prices'].pop(0)

                if len(DAILY_DATA[symbol]['prices']) == WINDOW_SIZE:
                    model = train_model(DAILY_DATA[symbol]['prices'])
                    next_price = predict_price(
                        model, len(DAILY_DATA[symbol]['prices']))
                    price_change = (
                        (next_price - current_price) / current_price) * 100
                    print(
                        f"Voorspelde prijsverandering voor {symbol}: {price_change:.2f}%")

                    if price_change > THRESHOLD and current_investment < MAX_TOTAL_INVESTMENT:
                        amount = 0.01
                        investable_amount = amount * current_price
                        if current_investment + investable_amount <= MAX_TOTAL_INVESTMENT:
                            record_transaction(
                                symbol, 'buy', amount, current_price)
                            current_investment += investable_amount
                            place_order(symbol, 'buy', amount, current_price)
                            print(
                                f"[INFO] Actie: Koopt {amount} {symbol.split('-')[0]}.")

                    elif price_change < -THRESHOLD:
                        balance = 0.01
                        record_transaction(
                            symbol, 'sell', balance, current_price)
                        current_investment -= balance * current_price
                        place_order(symbol, 'sell', balance, current_price)
                        print(
                            f"[INFO] Actie: Verkoopt {balance} {symbol.split('-')[0]}.")

                    else:
                        print("[INFO] Geen actie nodig.")

            print(f"Huidige investering: {current_investment:.2f} EUR")
            print(
                f"Resterend budget: {MAX_TOTAL_INVESTMENT - current_investment:.2f} EUR")
            print(f"Volgende run over {SLEEP_INTERVAL} seconden.")

            # Controleer of er een nieuwe dag is begonnen
            if time.time() - START_TIME >= 24 * 3600:
                daily_report()
                START_TIME = time.time()

            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        print("Trading bot gestopt.")
    except Exception as e:
        print(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    trading_bot()
