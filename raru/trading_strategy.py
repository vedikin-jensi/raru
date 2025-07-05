import tkinter as tk
from ttkbootstrap import Style, Window  # 🔁 UPDATED
from ttkbootstrap.widgets import Entry, Button as BootButton, Checkbutton  # 🔁 UPDATED
from tkinter import ttk
import requests

class TradingStrategyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Strategy")
        self.root.geometry("650x300")
        self.root.resizable(False, False)  

        # --- Custom Tab Bar ---
        tab_bar = tk.Frame(self.root, bg='white')
        tab_bar.pack(fill='x')
        self.strategy1_tab_btn = tk.Button(tab_bar, text='Strategy 1', font=('Segoe UI', 12, 'bold'), bd=0, padx=30, pady=8, relief='flat',
                                           command=lambda: self.show_tab(1))
        self.strategy2_tab_btn = tk.Button(tab_bar, text='Strategy 2', font=('Segoe UI', 12, 'bold'), bd=0, padx=30, pady=8, relief='flat',
                                           command=lambda: self.show_tab(2))
        self.strategy1_tab_btn.pack(side='left', padx=(10,0))
        self.strategy2_tab_btn.pack(side='left')

        self.strategy1_frame = tk.Frame(self.root, bg='white', highlightbackground='black', highlightthickness=1)
        self.strategy2_frame = tk.Frame(self.root, bg='white', highlightbackground='black', highlightthickness=1)

        self.setup_strategy1()
        self.setup_strategy2()

        self.show_tab(1)

    def show_tab(self, tab_index):
        if tab_index == 1:
            self.strategy2_frame.pack_forget()
            self.strategy1_frame.pack(fill='both', expand=True, padx=5, pady=5)
            self.strategy1_tab_btn.config(bg='#0074D9', fg='white', activebackground='#005fa3', activeforeground='white', relief='flat')
            self.strategy2_tab_btn.config(bg='white', fg='black', activebackground='#e6e6e6', activeforeground='black', relief='flat')
        else:
            self.strategy1_frame.pack_forget()
            self.strategy2_frame.pack(fill='both', expand=True, padx=5, pady=5)
            self.strategy2_tab_btn.config(bg='#0074D9', fg='white', activebackground='#005fa3', activeforeground='white', relief='flat')
            self.strategy1_tab_btn.config(bg='white', fg='black', activebackground='#e6e6e6', activeforeground='black', relief='flat')

    def setup_strategy1(self):
        strategy_frame = ttk.Frame(self.strategy1_frame)
        strategy_frame.pack(fill='x', padx=5, pady=5)

        # Fetch tickers from the Flask API
        def fetch_tickers():
            try:
                resp = requests.get("http://127.0.0.1:5000/tickers")
                data = resp.json()
                self.ticker_data = data['tickers']
                return [t['name'] for t in self.ticker_data]
            except Exception as e:
                print("Error fetching tickers:", e)
                self.ticker_data = [
                    {'symbol': 'CL', 'name': 'Crude Oil', 'exchange': 'NYMEX'},
                    {'symbol': 'BZ', 'name': 'Brent Crude', 'exchange': 'ICEEU'}
                ]
                return [t['name'] for t in self.ticker_data]

        ticker_values = fetch_tickers()
        self.ticker_var = tk.StringVar(value="Select Ticker")
        self.ticker_dropdown = ttk.Combobox(strategy_frame, textvariable=self.ticker_var, values=ticker_values, width=12, style='Blue.TCombobox')
        self.ticker_dropdown.grid(row=0, column=0, padx=5, pady=5)
        self.ticker_dropdown.configure(style='Blue.TCombobox')

        self.expiry_var = tk.StringVar(value="Select Expiry")
        self.expiry_dropdown = ttk.Combobox(strategy_frame, textvariable=self.expiry_var, values=[], width=12, style='Blue.TCombobox')
        self.expiry_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.expiry_dropdown.configure(style='Blue.TCombobox')

        def on_ticker_selected(event):
            selected_name = self.ticker_var.get()
            ticker = next((t for t in self.ticker_data if t['name'] == selected_name), None)
            if ticker:
                payload = {"symbol": ticker['symbol'], "exchange": ticker['exchange']}
                try:
                    exp_resp = requests.post("http://127.0.0.1:5000/expiries", json=payload)
                    exp_data = exp_resp.json()
                    expiry_values = exp_data.get('expiries', [])
                    self.expiry_var.set("Select Expiry")
                    self.expiry_dropdown['values'] = expiry_values
                except Exception as e:
                    print("Error fetching expiries:", e)
                    self.expiry_dropdown['values'] = []
            else:
                self.expiry_dropdown['values'] = []

        self.ticker_dropdown.bind("<<ComboboxSelected>>", on_ticker_selected)

        self.lot_entry = Entry(strategy_frame, width=12, bootstyle='primary')
        self.lot_entry.insert(0, "Enter Lot Size")
        self.lot_entry.config(foreground="gray")
        self.lot_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.lot_entry, "Enter Lot Size"))
        self.lot_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.lot_entry, "Enter Lot Size"))
        self.lot_entry.grid(row=0, column=2, padx=5, pady=5)

        self.tick_entry = Entry(strategy_frame, width=14, bootstyle='primary')
        self.tick_entry.insert(0, "Enter Tick Price")
        self.tick_entry.config(foreground="gray")
        self.tick_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.tick_entry, "Enter Tick Price"))
        self.tick_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.tick_entry, "Enter Tick Price"))
        self.tick_entry.grid(row=0, column=3, padx=5, pady=5)

        # --- Range Frame (Side by Side with spacing) ---
        self.range_from_entry = Entry(strategy_frame, width=12, bootstyle='primary')
        self.range_from_entry.insert(0, "Range From")
        self.range_from_entry.config(foreground="gray")
        self.range_from_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.range_from_entry, "Range From"))
        self.range_from_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.range_from_entry, "Range From"))
        self.range_from_entry.grid(row=0, column=4, padx=5, pady=5)

        self.range_to_entry = Entry(strategy_frame, width=12, bootstyle='primary')
        self.range_to_entry.insert(0, "Range To")
        self.range_to_entry.config(foreground="gray")
        self.range_to_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, self.range_to_entry, "Range To"))
        self.range_to_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, self.range_to_entry, "Range To"))
        self.range_to_entry.grid(row=1, column=4, padx=5, pady=5)

        self.active_var = tk.BooleanVar(value=True)
        active_switch = Checkbutton(strategy_frame, text="Active", variable=self.active_var, bootstyle='success,round-toggle')
        active_switch.grid(row=0, column=5, padx=10, pady=5)
        button_frame = ttk.Frame(strategy_frame)
        button_frame.grid(row=6, column=5, padx=5, pady=5, sticky="e")

        start_button = BootButton(
            button_frame, text="Start", style="PrimaryStart.TButton", command=self.start_strategy1, width=10
        )
        start_button.pack(side='top', pady=2, fill='x')

        reset_button = BootButton(
            button_frame, text="Reset", style="ResetDanger.TButton",
            width=10
        )
        reset_button.pack(side='top', pady=2, fill='x')



    # Placeholder Functions
    def clear_placeholder(self, event, entry, text):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def restore_placeholder(self, event, entry, text):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(foreground="gray")

    def setup_strategy2(self):
        # Fetch tickers from the Flask API for Strategy 2
        def fetch_tickers():
            try:
                resp = requests.get("http://127.0.0.1:5000/tickers")
                data = resp.json()
                self.strategy2_ticker_data = data['tickers']
                return [t['name'] for t in self.strategy2_ticker_data]
            except Exception as e:
                print("Error fetching tickers for Strategy 2:", e)
                self.strategy2_ticker_data = [
                    {'symbol': 'CL', 'name': 'Crude Oil', 'exchange': 'NYMEX'},
                    {'symbol': 'BZ', 'name': 'Brent Crude', 'exchange': 'ICEEU'}
                ]
                return [t['name'] for t in self.strategy2_ticker_data]

        crude_values = fetch_tickers()

        # Container frame to align dropdowns & entries into one column
        container_frame = tk.Frame(self.strategy2_frame, bg="#fdf5dc")
        container_frame.pack(fill='x', padx=5, pady=5)

        # --- FIRST ROW ---
        self.crude_var1 = tk.StringVar(value="Select Crude")
        self.crude_dropdown1 = ttk.Combobox(container_frame, textvariable=self.crude_var1, width=12, values=crude_values, style='Blue.TCombobox')
        self.crude_dropdown1.grid(row=0, column=0, padx=5, pady=5)
        self.crude_dropdown1.configure(style='Blue.TCombobox')

        self.expiry_var1 = tk.StringVar(value="Select Expiry")
        self.expiry_dropdown1 = ttk.Combobox(container_frame, textvariable=self.expiry_var1, values=[], width=12, style='Blue.TCombobox')
        self.expiry_dropdown1.grid(row=0, column=1, padx=5, pady=5)
        self.expiry_dropdown1.configure(style='Blue.TCombobox')

        def on_crude1_selected(event):
            selected_name = self.crude_var1.get()
            ticker = next((t for t in self.strategy2_ticker_data if t['name'] == selected_name), None)
            if ticker:
                payload = {"symbol": ticker['symbol'], "exchange": ticker['exchange']}
                try:
                    exp_resp = requests.post("http://127.0.0.1:5000/expiries", json=payload)
                    exp_data = exp_resp.json()
                    expiry_values = exp_data.get('expiries', [])
                    self.expiry_var1.set("Select Expiry")
                    self.expiry_dropdown1['values'] = expiry_values
                except Exception as e:
                    print("Error fetching expiries for Strategy 2 Row 1:", e)
                    self.expiry_dropdown1['values'] = []
            else:
                self.expiry_dropdown1['values'] = []

        self.crude_dropdown1.bind("<<ComboboxSelected>>", on_crude1_selected)

        # --- SECOND ROW ---
        self.crude_var2 = tk.StringVar(value="Select Crude")
        self.crude_dropdown2 = ttk.Combobox(container_frame, textvariable=self.crude_var2, width=12, values=crude_values, style='Blue.TCombobox')
        self.crude_dropdown2.grid(row=1, column=0, padx=5, pady=5)
        self.crude_dropdown2.configure(style='Blue.TCombobox')

        self.expiry_var2 = tk.StringVar(value="Select Expiry")
        self.expiry_dropdown2 = ttk.Combobox(container_frame, textvariable=self.expiry_var2, values=[], width=12, style='Blue.TCombobox')
        self.expiry_dropdown2.grid(row=1, column=1, padx=5, pady=5)
        self.expiry_dropdown2.configure(style='Blue.TCombobox')

        def on_crude2_selected(event):
            selected_name = self.crude_var2.get()
            ticker = next((t for t in self.strategy2_ticker_data if t['name'] == selected_name), None)
            if ticker:
                payload = {"symbol": ticker['symbol'], "exchange": ticker['exchange']}
                try:
                    exp_resp = requests.post("http://127.0.0.1:5000/expiries", json=payload)
                    exp_data = exp_resp.json()
                    expiry_values = exp_data.get('expiries', [])
                    self.expiry_var2.set("Select Expiry")
                    self.expiry_dropdown2['values'] = expiry_values
                except Exception as e:
                    print("Error fetching expiries for Strategy 2 Row 2:", e)
                    self.expiry_dropdown2['values'] = []
            else:
                self.expiry_dropdown2['values'] = []

        self.crude_dropdown2.bind("<<ComboboxSelected>>", on_crude2_selected)

        # Entries frame (Lot Size, Buy/Sell, Ratio)
        entries_frame = ttk.Frame(container_frame)
        entries_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5)  # Spanning across 2 rows

        self.lot_size1_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.lot_size1_entry.grid(row=0, column=0, padx=5, pady=5)
        self.lot_size1_entry.insert(0, "Lot Size")

        self.buy_sell1_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.buy_sell1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.buy_sell1_entry.insert(0, "Buy/Sell")

        self.ratio1_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.ratio1_entry.grid(row=0, column=2, padx=5, pady=5)
        self.ratio1_entry.insert(0, "Ratio")

        self.lot_size2_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.lot_size2_entry.grid(row=1, column=0, padx=5, pady=5)
        self.lot_size2_entry.insert(0, "Lot Size")

        self.buy_sell2_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.buy_sell2_entry.grid(row=1, column=1, padx=5, pady=5)
        self.buy_sell2_entry.insert(0, "Buy/Sell")

        self.ratio2_entry = ttk.Entry(entries_frame, width=8, foreground="gray")
        self.ratio2_entry.grid(row=1, column=2, padx=5, pady=5)
        self.ratio2_entry.insert(0, "Ratio")

        # View Arbitrage button
        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=10)  # Spanning across 2 rows

        self.view_button = BootButton(button_frame, text="View Arbitrage", style="Blue.TButton", command=self.view_arbitrage)
        self.view_button.pack(side='left', padx=5)

        self.arbitrage_frame = ttk.Frame(self.strategy2_frame)
        self.arbitrage_frame.pack(fill='x', padx=5, pady=5)
        self.arbitrage_frame.pack_forget()  # Hide initially

    
    def disable_strategy2_widgets(self):
        def disable_all_children(widget):
            for child in widget.winfo_children():
                # Apply disabled state and force grey style for comboboxes/entries
                if isinstance(child, ttk.Combobox):
                    child.config(state="disabled")
                    child.configure(style='Grey.TCombobox')
                elif isinstance(child, ttk.Entry):
                    child.config(state="disabled", foreground='black', background='#e0e0e0')
                elif isinstance(child, BootButton):
                    child.config(state="disabled", style='Disabled.TButton')
                elif isinstance(child, tk.Button):
                    child.config(state="disabled", bg='#e0e0e0', fg='black')
                elif isinstance(child, tk.Checkbutton):
                    child.config(state="disabled")
                disable_all_children(child)  # Recursively go into children

        disable_all_children(self.strategy2_frame)
        self.view_button.config(state="disabled", style='Disabled.TButton')
        if hasattr(self, 'place_order_button'):
            self.place_order_button.config(state="disabled", style='Disabled.TButton')

    def view_arbitrage(self):
    # Disable all widgets
        self.disable_strategy2_widgets()

        # Show Arbitrage and Target Arbitrage fields
        self.arbitrage_frame.pack(fill='x', padx=5, pady=5)

        # Arbitrage Details Row
        tk.Label(self.arbitrage_frame, text="Current Arbitrage:", font=("Segoe UI", 11, "bold"), fg="#0074D9").grid(row=0, column=0, padx=5, pady=5)
        self.current_arbitrage_label = tk.Label(self.arbitrage_frame, text="3.2", font=("Segoe UI", 11, "bold"), fg="#0074D9")
        self.current_arbitrage_label.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.arbitrage_frame, text="Target Arbitrage:", font=("Segoe UI", 11, "bold"), fg="#0074D9").grid(row=0, column=2, padx=5, pady=5)
        self.target_arbitrage_entry = ttk.Entry(self.arbitrage_frame, width=10, foreground='black', background='#e0e0e0')
        self.target_arbitrage_entry.grid(row=0, column=3, padx=5, pady=5)
        self.target_arbitrage_entry.insert(0, "3.5")

    # Place Order Button
        self.place_order_button = BootButton(self.arbitrage_frame, text="Place Order", style="Blue.TButton", command=self.place_order)
        self.place_order_button.grid(row=0, column=4, padx=5, pady=5)

    def place_order(self):
    # Disable the Target Arbitrage entry and Place Order button
        self.target_arbitrage_entry.config(state="disabled")
        self.place_order_button.config(state="disabled", style='Disabled.TButton')

        # ---- New Row UI: Entries with Placeholders ---- #
        self.extra_row_frame = ttk.Frame(self.arbitrage_frame)
        self.extra_row_frame.grid(row=1, column=0, columnspan=8, pady=10)

        # Range From Entry with Placeholder
        self.range_from_entry = ttk.Entry(self.extra_row_frame, width=12, foreground="gray")
        self.range_from_entry.insert(0, "Range From")
        self.range_from_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, self.range_from_entry, "Range From"))
        self.range_from_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, self.range_from_entry, "Range From"))
        self.range_from_entry.grid(row=0, column=0, padx=5)

        # Range To Entry with Placeholder
        self.range_to_entry = ttk.Entry(self.extra_row_frame, width=12, foreground="gray")
        self.range_to_entry.insert(0, "Range To")
        self.range_to_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, self.range_to_entry, "Range To"))
        self.range_to_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, self.range_to_entry, "Range To"))
        self.range_to_entry.grid(row=0, column=1, padx=5)

        # Tick Size Entry with Placeholder
        self.tick_size_entry = ttk.Entry(self.extra_row_frame, width=12, foreground="gray")
        self.tick_size_entry.insert(0, "Tick Size")
        self.tick_size_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, self.tick_size_entry, "Tick Size"))
        self.tick_size_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, self.tick_size_entry, "Tick Size"))
        self.tick_size_entry.grid(row=0, column=2, padx=5)

        # Toggle Button (Active / Inactive)
        self.is_active = tk.BooleanVar(value=False)
        self.active_button = tk.Checkbutton(self.extra_row_frame, text="Active", variable=self.is_active, onvalue=True, offvalue=False)
        self.active_button.grid(row=0, column=3, padx=10)

        # Start Button
        # Align Active switch and Start button in a horizontal frame
        active_start_frame = ttk.Frame(self.extra_row_frame)
        active_start_frame.grid(row=0, column=3, columnspan=2, padx=10, sticky="w")

        self.active_button = tk.Checkbutton(active_start_frame, text="Active", variable=self.is_active, onvalue=True, offvalue=False)
        self.active_button.pack(side="left", padx=(0, 10))

        self.start_button = BootButton(active_start_frame, text="Start", style="Blue.TButton", command=self.start_process, width=8)
        self.start_button.pack(side="left")


    def start_process(self):
        print("Start button clicked.")
        print(f"Range From: {self.range_from_entry.get()}")
        print(f"Range To: {self.range_to_entry.get()}")
        print(f"Tick Size: {self.tick_size_entry.get()}")
        print(f"Active: {self.is_active.get()}") 



    def start_strategy1(self):
        pass

    def reset_strategy1(self):
        # Reset dropdowns
        self.ticker_var.set('Select Ticker')
        self.expiry_var.set('Select Expiry')

        # Reset entries with placeholders
        self.lot_entry.delete(0, tk.END)
        self.lot_entry.insert(0, "Enter Lot Size")

        self.tick_entry.delete(0, tk.END)
        self.tick_entry.insert(0, "Enter Tick Price")
        

        self.range_from_entry.delete(0, tk.END)
        self.range_from_entry.insert(0, "Range From")

        self.range_to_entry.delete(0, tk.END)
        self.range_to_entry.insert(0, "Range To")

        # Reset toggle
        self.active_var.set(True)

    
if __name__ == "__main__":
    root = Window(themename="flatly")  
    style = Style()
    # Set global font and padding for a modern look
    style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)
    style.configure('TCombobox', font=('Segoe UI', 12), padding=5)
    style.configure(
        'Blue.TButton',
        font=('Segoe UI', 11, 'bold'),
        background='#0074D9',
        foreground='white',
        borderwidth=0,
        focusthickness=3,
        focuscolor='none',
        padding=4,
        relief='flat',
        bordercolor='#0074D9',
        borderradius=8
    )
    style.configure(
        'Disabled.TButton',
        font=('Segoe UI', 11, 'bold'),
        background='#f1f1f1',  # lighter top
        foreground='#222222',
        borderwidth=2,
        focusthickness=3,
        focuscolor='none',
        padding=4,
        relief='groove',  # gives a subtle 3D effect
        bordercolor='#b0b0b0',
        borderradius=8,
        lightcolor='#ffffff',
        darkcolor='#e0e0e0'
    )
    style.map(
        'Blue.TButton',
        background=[('active', '#005fa3')],
        foreground=[('active', 'white')]
    )
    style.configure(
        'Blue.TCombobox',
        fieldbackground='#0074D9',  # blue background
        background='#0074D9',       # blue dropdown arrow
        foreground='white',
        arrowcolor='white',  # ensure arrow color is white
        selectforeground='white',     # selected text color
        selectbackground='#0074D9',   # background after selection
        bordercolor='#0074D9',
        lightcolor='#0074D9',
        darkcolor='#0074D9',
        borderwidth=1,
        relief='flat',
        borderradius=8
    )
    style.configure(
        'Grey.TCombobox',
        fieldbackground='#f1f1f1',
        background='#f1f1f1',
        foreground='#222222',
        arrowcolor='#222222',
        selectforeground='#222222',
        selectbackground='#f1f1f1',
        bordercolor='#b0b0b0',
        lightcolor='#ffffff',
        darkcolor='#e0e0e0',
        borderwidth=2,
        relief='groove',
        borderradius=8,
        font=('Segoe UI', 11, 'bold')
    )
    style.configure('TEntry', font=('Segoe UI', 12), padding=5)
    style.configure(
    'PrimaryStart.TButton',
    font=('Segoe UI', 12, 'bold'),
    background='#0074D9',
    foreground='white',
    borderwidth=0,
    focusthickness=3,
    focuscolor='none'
    )
    style.map(
        'PrimaryStart.TButton',
        background=[('active', '#005fa3')],
        foreground=[('active', 'white')]
    )
    style.configure(
    'ResetDanger.TButton',
    font=('Segoe UI', 12, 'bold'),
    background='#FF4136',
    foreground='white',
    borderwidth=0,
    relief='flat',
    )
    style.map(
        'ResetDanger.TButton',
        background=[('active', '#cc3329')],
        foreground=[('active', 'white')]
    )
    style.configure(
    'Disabled.TButton',
    font=('Segoe UI', 11, 'bold'),
    background='#f1f1f1',
    foreground='#222222',
    borderwidth=2,
    focusthickness=3,
    focuscolor='none',
    padding=4,
    relief='groove',  # subtle 3D effect
    bordercolor='#b0b0b0',
    borderradius=8,
    lightcolor='#ffffff',
    darkcolor='#e0e0e0'
    )
    app = TradingStrategyApp(root)
    root.mainloop()