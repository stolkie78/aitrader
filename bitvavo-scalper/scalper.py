from python_bitvavo_api.bitvavo import Bitvavo
from sklearn.linear_model import LinearRegression
import requests
import json
import numpy as np
import time
from datetime import datetime
import os
from decimal import Decimal

#Meta info
BOTNAME = "BAIBY"
version = "0.8"

# Configuratiebestanden
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)



# Laad configuratie vanuit JSON-bestand
def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

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
bitvavo = Bitvavo({
    'APIKEY': config.get('API_KEY'),
    'APISECRET': config.get('API_SECRET'),
    'RESTURL': config.get('RESTURL', 'https://api.bitvavo.com/v2'),
    'WSURL': config.get('WSURL', 'wss://ws.bitvavo.com/v2/'),
    'ACCESSWINDOW': config.get('ACCESSWINDOW', 10000),
    'DEBUGGING': config.get('DEBUGGING', False)
})

# Configuratie laden uit slack.json
slack_config = load_config('slack.json')
SLACK_WEBHOOK_URL = slack_config.get("SLACK_WEBHOOK_URL")
print(f"Slack configuratie: {slack_config}")

# Configuratie laden vanuit trader.json
scalper_config = load_config('scalper.json')
SYMBOL = scalper_config.get("SYMBOL")
THRESHOLD_BUY = scalper_config.get("THRESHOLD_BUY")
THRESHOLD_SELL = scalper_config.get("THRESHOLD_SELL")
STOP_LOSS = scalper_config.get("STOP_LOSS")
TRADE_AMOUNT = scalper_config.get("TRADE_AMOUNT")
CHECK_INTERVAL = scalper_config.get("CHECK_INTERVAL")
DEMO_MODE = scalper_config.get("DEMO_MODE")
WINDOW_SIZE = scalper_config.get("WINDOW_SIZE", 10)

# Status en transacties laden/opslaan
STATUS_FILE = os.path.join(DATA_DIR, f"status_{SYMBOL}.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, f"transactions_{SYMBOL}.log")

# Status en transacties laden
status = load_status(STATUS_FILE)
transactions = load_transactions(TRANSACTIONS_FILE)
price_history = []  # Historische prijzen
start_time = datetime.now()  # Starttijd voor dagelijkse rapportage

    # Slack-bericht sturen
def send_to_slack(message):
    payload= {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[FOUT] Kon bericht niet naar Slack sturen: {e}")

# Logfunctie
def log_message(message):
    if DEMO_MODE:
        RUNSTATUS = "[DEMO]"
    else:
        RUNSTATUS = "[PROD]"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{RUNSTATUS}[SCALPER][{SYMBOL}][{timestamp}] {BOTNAME} {message}")
    send_to_slack(f"{RUNSTATUS}[SCALPER][{SYMBOL}] {message}")

def get_current_price(symbol):
    """Haal de huidige prijs op."""
    ticker = bitvavo.tickerPrice({'market': symbol})
    if 'price' not in ticker:
        log_message(f"[ERROR] Kon de prijs niet ophalen voor {symbol}.")
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

    log_message(f"[INFO] Dagelijkse winst/verlies: {total_profit_loss:.2f} EUR")
    return total_profit_loss


def place_order(symbol, side, amount, price):
    """Plaats een order of toon een simulatie in demo-modus."""
    if DEMO_MODE:
        log_message(f"[DEMO] {side.capitalize()} {amount:.6f} {symbol.split('-')[0]} tegen {price:.2f} EUR.")
    else:
        try:
            order = bitvavo.placeOrder(symbol, side, 'market', {'amount': str(amount)})
            print(f"[INFO] Order geplaatst: {order}")
        except Exception as e:
            log_message(f"[ERROR] Fout bij het plaatsen van de order: {e}")


# Kosten per trade in percentage
TRADE_FEE_PERCENTAGE = 0.5  # Bijvoorbeeld 0.5% kosten


def calculate_trade_cost(price, amount):
    """Bereken de handelskosten."""
    return (TRADE_FEE_PERCENTAGE / 100) * price * amount


def trading_bot():
    """Scalping bot met AI-predictie, handelskosten en winstvalidatie."""
    global status, start_time
    try:
        while True:
            current_price = get_current_price(SYMBOL)
            price_history.append(current_price)

            # Behoud alleen de laatste WINDOW_SIZE prijzen
            if len(price_history) > WINDOW_SIZE:
                price_history.pop(0)

            print(f"Huidige prijs: {current_price:.2f}")

            # Alleen trainen als we genoeg data hebben
            if len(price_history) == WINDOW_SIZE:
                model = train_model(price_history)
                next_price = predict_price(model, len(price_history))
                price_change = ((next_price - current_price) /
                                current_price) * 100

                # Minimale winst om break-even te draaien
                trade_cost = calculate_trade_cost(current_price, TRADE_AMOUNT)
                minimum_profit = 2 * trade_cost  # Kosten bij kopen en verkopen

                print(
                    f"Voorspelde prijs: {next_price:.2f} EUR | Verandering: {price_change:.2f}% | "
                    f"Minimale winst vereist: {minimum_profit:.2f} EUR"
                )

                if not status["open_position"] and next_price > current_price + minimum_profit:
                    # Kooppositie openen
                    log_message(
                        f":green_apple: Koopt {TRADE_AMOUNT} BTC (verwachte winst > kosten).")
                    place_order(SYMBOL, 'buy', TRADE_AMOUNT, current_price)
                    record_transaction('buy', TRADE_AMOUNT, current_price)
                    status.update(
                        {"last_action": "buy", "buy_price": current_price, "open_position": True})
                    save_status(STATUS_FILE, status)

                elif status["open_position"]:
                    # Controleer winst of verlies
                    profit_loss = (
                        (current_price - status["buy_price"]) / status["buy_price"]) * 100
                    if profit_loss > THRESHOLD_SELL and current_price - status["buy_price"] > minimum_profit:
                        log_message(
                            f":apple: Verkoopt {TRADE_AMOUNT} BTC (+{profit_loss:.2f}% winst).")
                        place_order(SYMBOL, 'sell',
                                    TRADE_AMOUNT, current_price)
                        record_transaction('sell', TRADE_AMOUNT, current_price)
                        status.update(
                            {"last_action": "sell", "buy_price": None, "open_position": False})
                        save_status(STATUS_FILE, status)

                    elif profit_loss < STOP_LOSS:
                        log_message(
                            f":meat_on_bone: Verkoopt {TRADE_AMOUNT} BTC (stop-loss bereikt).")
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
        log_message("[INFO] Trading bot gestopt door gebruiker.")
        generate_daily_report()
    except Exception as e:
        log_message(f"Fout: {e}")


# Start de bot
if __name__ == "__main__":
    log_message(f"[INFO] Scalping bot {version} gestart")
    log_message(f"Configuratie: {scalper_config}")
    if status["open_position"]:
        open_buy_price = status["buy_price"]
        print(f"Reeds openstaande positie voor {SYMBOL} gekocht voor {open_buy_price}")
    trading_bot()
