# api.py
from flask import Flask, request, jsonify
from ib_insync import IB, Future

import asyncio

# Ensure global event loop exists in main thread
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Ensure event loop exists in every thread

def ensure_event_loop():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

from flask import Flask
app = Flask(__name__)

# Initialize and connect to TWS (demo/read‑only mode warnings are normal)
ib = IB()

# Try connecting with a range of clientIds to avoid 'already in use' errors
connected = False
for client_id in range(102, 111):  # Try 100, 101, ..., 109
    try:
        print(f"Trying to connect to TWS with clientId={client_id}...")
        ib.connect('127.0.0.1', 7497, clientId=client_id)
        # When connecting, after a successful connection:
        connected_client_id = client_id 
        print(f"Connected to TWS with clientId={connected_client_id}!")
        connected = True
        break
    except Exception as e:
        print(f"Could not connect with clientId={client_id}: {e}")
if not connected:
    print("ERROR: Could not connect to TWS on any clientId in range 100-109. Make sure TWS is running and API is enabled.")
    exit(1)

# Example tickers (expand as needed)
SUPPORTED_TICKERS = [
    {'symbol': 'CL', 'name': 'Crude Oil', 'exchange': 'NYMEX'},
    {'symbol': 'BZ', 'name': 'Brent Crude', 'exchange': 'ICEEU'}
]



@app.route('/tickers', methods=['GET'])
def get_tickers():
    # Example: Fetch all active crude oil and brent futures from IB
    # You can customize this logic for other asset types as needed
    ensure_event_loop()
    try:
        crude_contracts = ib.reqContractDetails(Future(symbol='CL', exchange='NYMEX'))
        brent_contracts = ib.reqContractDetails(Future(symbol='BZ', exchange='NYMEX', currency='USD'))
        print("Crude contracts:", crude_contracts)
        print("Brent contracts:", brent_contracts)

        tickers = []
        # Add crude oil futures
        for c in crude_contracts:
            tickers.append({
                'symbol': c.contract.symbol,
                'name': c.contract.localSymbol,
                'exchange': c.contract.exchange,
                'expiry': c.contract.lastTradeDateOrContractMonth
            })
        # Add brent crude futures
        for c in brent_contracts:
            tickers.append({
                'symbol': c.contract.symbol,
                'name': c.contract.localSymbol,
                'exchange': c.contract.exchange,
                'expiry': c.contract.lastTradeDateOrContractMonth
            })
        return jsonify({'tickers': tickers})
    except Exception as e:
        print("Error in /tickers:", e)
        return jsonify({'tickers': [], 'error': str(e)})



@app.route('/expiries', methods=['POST'])
def get_expiries():
    ensure_event_loop()
    data = request.get_json(force=True)
    symbol = data.get('symbol')
    exchange = data.get('exchange')
    if not symbol or not exchange:
        return jsonify(expiries=[], error='Missing symbol or exchange'), 400
    try:
        contracts = ib.reqContractDetails(Future(symbol=symbol, exchange=exchange, currency='USD'))
        # Extract unique expiry months
        expiries = list({c.contract.lastTradeDateOrContractMonth for c in contracts if c.contract.lastTradeDateOrContractMonth})
        expiries = sorted(expiries)
        return jsonify({'expiries': expiries, 'error': None})
    except Exception as e:
        print("Error in /expiries:", e)
        return jsonify(expiries=[], error=str(e)), 500





# For backward compatibility, keep the old endpoint but generalize it
def get_exchange_for_ticker(ticker):
    for t in SUPPORTED_TICKERS:
        if t['name'].lower() == ticker.lower() or t['symbol'].lower() == ticker.lower():
            return t['exchange'], t['symbol']
    return None, None

# @app.route('/ticker-details', methods=['POST'])
# def ticker_details():
#     data = request.get_json(force=True)
#     ticker = data.get('ticker_text')
#     exchange, symbol = get_exchange_for_ticker(ticker)
#     if not exchange or not symbol:
#         return jsonify(expiries=[], error=f'Unsupported ticker {ticker}'), 400
#     contract = Future(symbol=symbol, exchange=exchange, currency='USD')
#     try:
#         details = ib.run(ib.reqContractDetails(contract))

#         # Month‑number to name mapping
#         month_names = {
#             '01': 'January', '02': 'February', '03': 'March',
#             '04': 'April',   '05': 'May',      '06': 'June',
#             '07': 'July',    '08': 'August',   '09': 'September',
#             '10': 'October', '11': 'November', '12': 'December'
#         }

#         expiries = []
#         for d in details:
#             ym = d.contract.contractMonth  # e.g. "202501"
#             year, mon = ym[:4], ym[4:]
#             if mon in month_names:
#                 expiries.append(f"{year} {month_names[mon]}")
#         expiries.sort()

#         return jsonify(expiries=expiries, error=None)

#     except Exception as e:
#         return jsonify(expiries=[], error=str(e)), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=False)
