from ib_insync import *

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

# Define Forex contract correctly
contract = Forex('EURUSD')  # Not Stock

# Qualify the contract (ensures it's recognized by IB)
ib.qualifyContracts(contract)

# Request live market data (streaming, not snapshot)
ticker = ib.reqMktData(contract, '', False, False)

# Wait for data to come in
ib.sleep(2)

# Use fallback for mid if last price is unavailable (common in Forex)
mid = (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None

print(f"Symbol: {contract.symbol}")
print(f"Last Price: {ticker.last}")
print(f"Bid: {ticker.bid}, Ask: {ticker.ask}, Mid: {mid}")

# Disconnect from IB
ib.disconnect()
