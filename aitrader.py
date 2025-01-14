from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import numpy as np
import time

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
SYMBOLS = ['BTC-EUR', 'ETH-EUR']  # Lijst van munten
WINDOW_SIZE = 10  # Aantal datapunten voor historische analyse
THRESHOLD = 2  # Percentage prijsverandering voor koop/verkoopbeslissingen
MAX_TOTAL_INVESTMENT = 1000  # Maximum totaal investeringsbedrag in EUR
current_investment = 0  # Houdt bij hoeveel er momenteel is geïnvesteerd
DAILY_DATA = {symbol: {'transactions': [], 'prices': []} for symbol in SYMBOLS}
START_TIME = time.time()


def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
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
            # Winst/verlies = (verkoopprijs - gemiddelde aankoopprijs) * hoeveelheid
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


def trading_bot():
    """Trading bot met dagelijkse winst/verlies rapportage en max trading bedrag."""
    global current_investment, START_TIME

    try:
        while True:
            for symbol in SYMBOLS:
                current_price = get_current_price(symbol)
                print(f"Huidige prijs van {symbol}: {current_price:.2f} EUR")
                DAILY_DATA[symbol]['prices'].append(current_price)

                # Behoud alleen de laatste `WINDOW_SIZE` prijzen
                if len(DAILY_DATA[symbol]['prices']) > WINDOW_SIZE:
                    DAILY_DATA[symbol]['prices'].pop(0)

                # Train een model en maak een voorspelling
                if len(DAILY_DATA[symbol]['prices']) == WINDOW_SIZE:
                    model = train_model(DAILY_DATA[symbol]['prices'])
                    next_price = predict_price(
                        model, len(DAILY_DATA[symbol]['prices']))
                    price_change = (
                        (next_price - current_price) / current_price) * 100
                    print(
                        f"Voorspelde prijsverandering voor {symbol}: {price_change:.2f}%")

                    # Koop of verkoop op basis van voorspelling
                    if price_change > THRESHOLD and current_investment < MAX_TOTAL_INVESTMENT:
                        amount = 0.01  # Koop een kleine hoeveelheid
                        investable_amount = amount * current_price
                        if current_investment + investable_amount <= MAX_TOTAL_INVESTMENT:
                            record_transaction(
                                symbol, 'buy', amount, current_price)
                            current_investment += investable_amount
                            print(
                                f"Koop {amount} {symbol.split('-')[0]} tegen {current_price:.2f} EUR.")

                    elif price_change < -THRESHOLD:
                        balance = 0.01  # Stel dat we 0.01 van de munt hebben
                        record_transaction(
                            symbol, 'sell', balance, current_price)
                        current_investment -= balance * current_price
                        print(
                            f"Verkoop {balance} {symbol.split('-')[0]} tegen {current_price:.2f} EUR.")

            # Controleer of er een nieuwe dag is begonnen
            if time.time() - START_TIME >= 24 * 3600:
                daily_report()
                START_TIME = time.time()  # Reset de starttijd voor de nieuwe dag

            time.sleep(60)  # Wacht 1 minuut voor de volgende iteratie
    except KeyboardInterrupt:
        print("Trading bot gestopt.")
    except Exception as e:
        print(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    trading_bot()
