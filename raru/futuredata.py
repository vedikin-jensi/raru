from ib_insync import *
import tkinter as tk
from tkinter import ttk, messagebox

# Initialize IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

# Mapping of symbols to exchanges
symbol_exchange_map = {
    'CL': 'NYMEX',  # Crude Oil
    'BZ': 'ICEEU'   # Brent Crude
}

# Function to update expiry months based on selected symbol
def update_expiry_months(event):
    selected_symbol = symbol_var.get()
    exchange = symbol_exchange_map.get(selected_symbol)
    if not exchange:
        messagebox.showerror("Error", f"No exchange found for symbol {selected_symbol}")
        return

    # Request contract details to get available expiry months
    contracts = ib.reqContractDetails(Future(symbol=selected_symbol, exchange=exchange, currency='USD'))
    expiry_months = sorted(set(cd.contract.lastTradeDateOrContractMonth for cd in contracts))
    expiry_dropdown['values'] = expiry_months
    expiry_var.set('')  # Clear previous selection

# Function to display contract details based on selected symbol and expiry
def display_contract_details(event):
    selected_symbol = symbol_var.get()
    selected_expiry = expiry_var.get()
    exchange = symbol_exchange_map.get(selected_symbol)
    if not exchange or not selected_expiry:
        messagebox.showerror("Error", "Please select both symbol and expiry month.")
        return

    # Define the futures contract
    contract = Future(symbol=selected_symbol, lastTradeDateOrContractMonth=selected_expiry, exchange=exchange, currency='USD')
    ib.qualifyContracts(contract)
    details = ib.reqContractDetails(contract)
    if not details:
        messagebox.showerror("Error", "Contract details not found.")
        return

    detail = details[0]
    lot_size = detail.contract.multiplier
    tick_size = detail.minTick

    result_text.set(f"Symbol: {selected_symbol}\nExpiry: {selected_expiry}\nExchange: {exchange}\nLot Size: {lot_size}\nTick Size: {tick_size}")

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Futures Contract Selector")

# Symbol Dropdown
tk.Label(root, text="Select Symbol:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
symbol_var = tk.StringVar()
symbol_dropdown = ttk.Combobox(root, textvariable=symbol_var, state="readonly")
symbol_dropdown['values'] = list(symbol_exchange_map.keys())
symbol_dropdown.bind("<<ComboboxSelected>>", update_expiry_months)
symbol_dropdown.grid(row=0, column=1, padx=10, pady=10)

# Expiry Month Dropdown
tk.Label(root, text="Select Expiry Month:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
expiry_var = tk.StringVar()
expiry_dropdown = ttk.Combobox(root, textvariable=expiry_var, state="readonly")
expiry_dropdown.bind("<<ComboboxSelected>>", display_contract_details)
expiry_dropdown.grid(row=1, column=1, padx=10, pady=10)

# Result Display
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify='left').grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI loop
root.mainloop()

# Disconnect IB connection when GUI is closed
ib.disconnect()
