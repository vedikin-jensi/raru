from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QCheckBox, QPushButton, QFrame, QGridLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt
import sys
import json
from window_manager import WindowManager
from ib_insync import *

class PlaceholderLineEdit(QLineEdit):
    def __init__(self, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.setText(self.placeholder)
        self.setStyleSheet("""
            QLineEdit {
                color: gray;
                border: 1px solid #aaa;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.is_placeholder = True

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.text() == self.placeholder:
            self.clear()
            self.setStyleSheet("""
                QLineEdit {
                    color: black;
                    border: 1px solid #4169e1;
                    border-radius: 6px;
                    padding: 6px;
                }
            """)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if not self.text():
            self.setText(self.placeholder)
            self.setStyleSheet("""
                QLineEdit {
                    color: gray;
                    border: 1px solid #aaa;
                    border-radius: 6px;
                    padding: 6px;
                }
            """)

class TradingStrategyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Strategy")
        
        # Initialize IB connection
        self.ib = IB()
        try:
            self.ib.connect('127.0.0.1', 7497, clientId=2)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", 
                               "Could not connect to TWS. Please ensure TWS is running.")
            sys.exit(1)
            
        # Symbol to exchange mapping
        self.symbol_exchange_map = {
            'CL': 'NYMEX',  # Crude Oil
            'BZ': 'NYMEX'     # Brent Crude
          
        }
        
        # Symbol display names to actual symbols
        self.symbol_map = {
           
            'Crude': 'CL',
            'Brent': 'BZ',
           
        }
        
        # Initialize expiry mapping dictionary
        self.expiry_mapping = {}
        
        layout = QVBoxLayout(self)

        # Logout button
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setStyleSheet("""
            QPushButton {
                background-color: #2d5ca6;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 16px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #1e3d70;
            }
        """)
        self.change_password_button.clicked.connect(self.show_change_password)
        header_layout.addWidget(self.change_password_button)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: crimson;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #dc143c;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
    QTabBar::tab {
    
        color: black;
        width: 100px;
        height: 30px;
       
        font-weight: bold;
    }

    QTabBar::tab:selected {
        background: royalblue;
        color: white;
    }
""")
        layout.addWidget(self.tabs)

        self.strategy1_tab = QWidget()
        self.strategy2_tab = QWidget()
        self.tabs.addTab(self.strategy1_tab, "Strategy 1")
        self.tabs.addTab(self.strategy2_tab, "Strategy 2")

        self.setup_strategy1()
        self.setup_strategy2()

        qr = self.frameGeometry()
        cp = QApplication.desktop().screen().rect().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_strategy1(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        self.strategy1_tab.setLayout(layout)

        # Common ComboBox style
        combo_style = """
        QComboBox {
            border: 1px solid gray;
            border-radius: 8px;
            padding: 6px 12px;
            background-color: white;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-radius: 0px;
        }
        QComboBox::down-arrow {
            image: url(./icons/image.png);
            width: 10px;
            height: 10px;
        }
        """

        self.ticker_combo = QComboBox()
        self.ticker_combo.addItems(["Select Ticker"] + list(self.symbol_map.keys()))
        self.ticker_combo.setFixedHeight(30)
        self.ticker_combo.setStyleSheet(combo_style)
        self.ticker_combo.currentTextChanged.connect(self.on_ticker_changed)
        layout.addWidget(self.ticker_combo, 0, 0)

        self.expiry_combo = QComboBox()
        self.expiry_combo.addItem("Select Expiry")
        self.expiry_combo.setFixedHeight(30)
        self.expiry_combo.setStyleSheet(combo_style)
        self.expiry_combo.currentTextChanged.connect(self.on_expiry_changed)
        layout.addWidget(self.expiry_combo, 0, 1)

        self.lot_entry = PlaceholderLineEdit("Lot Size")
        self.lot_entry.setMinimumWidth(100)
        self.lot_entry.setReadOnly(True)
        layout.addWidget(self.lot_entry, 0, 2)

        self.tick_entry = PlaceholderLineEdit("Tick Price")
        self.tick_entry.setMinimumWidth(100)
        self.tick_entry.setReadOnly(True)
        layout.addWidget(self.tick_entry, 0, 3)
        
        self.range_from_entry = PlaceholderLineEdit("Range From")
        self.range_to_entry = PlaceholderLineEdit("Range To")
        self.range_from_entry.setMinimumWidth(100)
        self.range_to_entry.setMinimumWidth(100)
        range_layout = QVBoxLayout()
        range_layout.addWidget(self.range_from_entry)
        range_layout.addWidget(self.range_to_entry)
        range_frame = QFrame()
        range_frame.setLayout(range_layout)
        layout.addWidget(range_frame, 0, 4)

        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setChecked(True)
        layout.addWidget(self.active_checkbox, 0, 5)

        self.start_button1 = QPushButton("Start")
        self.start_button1.setStyleSheet("""
            QPushButton {
                background-color: royalblue;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4169e1;
            }
        """)
        layout.addWidget(self.start_button1, 1, 5)

        self.reset_button1 = QPushButton("Reset")
        self.reset_button1.setStyleSheet("""
            QPushButton {
                background-color: crimson;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #dc143c;
            }
        """)
        layout.addWidget(self.reset_button1, 2, 5)
        self.reset_button1.clicked.connect(self.reset_strategy1)

    def setup_strategy2(self):
        layout = QVBoxLayout(self.strategy2_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        self.combo_grid = QGridLayout()
        layout.addLayout(self.combo_grid)

        # ComboBox style to match PlaceholderLineEdit
        combo_style = """
        QComboBox {
            border: 1px solid gray;
            border-radius: 8px;
            padding: 6px 12px;
            background-color: white;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-radius: 0px;
        }
        QComboBox::down-arrow {
            image: url(./icons/image.png);
            width: 12px;
        height: 12px;
    }
        """

        crude_options = ["Crude", "Brent", "Others"]
        expiry_options = ["Select Expiry", "1", "2", "3", "4"]

        # First row dropdowns
        self.crude_combo1 = QComboBox()
        self.crude_combo1.addItems(crude_options)
        self.crude_combo1.setStyleSheet(combo_style)
        self.crude_combo1.setFixedHeight(30)

        self.expiry_combo1 = QComboBox()
        self.expiry_combo1.addItems(expiry_options)
        self.expiry_combo1.setStyleSheet(combo_style)
        self.expiry_combo1.setFixedHeight(30)

        self.combo_grid.addWidget(self.crude_combo1, 0, 0)
        self.combo_grid.addWidget(self.expiry_combo1, 0, 1)

        # Second row dropdowns
        self.crude_combo2 = QComboBox()
        self.crude_combo2.addItems(crude_options)
        self.crude_combo2.setStyleSheet(combo_style)
        self.crude_combo2.setFixedHeight(30)

        self.expiry_combo2 = QComboBox()
        self.expiry_combo2.addItems(expiry_options)
        self.expiry_combo2.setStyleSheet(combo_style)
        self.expiry_combo2.setFixedHeight(30)

        self.combo_grid.addWidget(self.crude_combo2, 1, 0)
        self.combo_grid.addWidget(self.expiry_combo2, 1, 1)

        # Input fields: Lot Size, Buy/Sell, Ratio
        self.entries = []
        for row in range(2):
            for col in range(3):
                placeholder = ["Lot Size", "Buy/Sell", "Ratio"][col]
                entry = PlaceholderLineEdit(placeholder)
                self.combo_grid.addWidget(entry, row, col + 2)
                self.entries.append(entry)

        # View Arbitrage button
        self.view_button = QPushButton("View Arbitrage")
        self.view_button.setFixedWidth(130)
        self.view_button.setMinimumHeight(30)
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: royalblue;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4169e1;
            }
            QPushButton:disabled {
                background-color: lightgray;
                color: white;
            }
        """)
        self.view_button.clicked.connect(self.view_arbitrage)
        self.combo_grid.addWidget(self.view_button, 0, 6, 2, 1)

        # Arbitrage result frame
        self.arbitrage_frame = QGridLayout()
        self.arbitrage_widget = QWidget()
        self.arbitrage_widget.setLayout(self.arbitrage_frame)
        self.arbitrage_widget.setVisible(False)
        layout.addWidget(self.arbitrage_widget)


    def view_arbitrage(self):
        self.view_button.setDisabled(True)
        self.disable_strategy2_widgets()
        self.arbitrage_widget.setVisible(True)

        self.arbitrage_widget.setStyleSheet("""
            border-radius: 10px;
         
        """)

        label_style = "color: #4169e1; font-weight: bold;"
        input_style = """
            QLineEdit {
                border: 1px solid #aaa;
                border-radius: 6px;
             
                background-color: white;
            }
        """
        button_style = """
            QPushButton {
                background-color: royalblue;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #4169e1;
            }
            QPushButton:disabled {
                background-color: lightgray;
                color: white;
            }
        """

        while self.arbitrage_frame.count():
            child = self.arbitrage_frame.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        current_label = QLabel("Current Arbitrage:")
        current_label.setStyleSheet(label_style)
        current_value = QLabel("3.2")
        current_value.setStyleSheet(label_style)

        target_label = QLabel("Target Arbitrage:")
        target_label.setStyleSheet(label_style)

        self.target_arb_entry = QLineEdit("3.5")
        self.target_arb_entry.setFixedWidth(100)
        self.target_arb_entry.setStyleSheet(input_style)

        self.place_button = QPushButton("Place Order")
        self.place_button.setStyleSheet(button_style)
        self.place_button.clicked.connect(self.place_order)

        self.arbitrage_frame.addWidget(current_label, 0, 0)
        
        self.arbitrage_frame.addWidget(current_value, 0, 1)
        self.arbitrage_frame.addWidget(target_label, 0, 2)
        self.arbitrage_frame.addWidget(self.target_arb_entry, 0, 3)
        self.arbitrage_frame.addWidget(self.place_button, 0, 6)

    def place_order(self):
        self.target_arb_entry.setDisabled(True)
        self.place_button.setDisabled(True)
        self.place_button.setFixedWidth(130) 
        

        self.extra_range_frame = QGridLayout()
        self.arbitrage_frame.addLayout(self.extra_range_frame, 1, 0, 1, 7)

        self.range_from = PlaceholderLineEdit("Range From")
        self.range_from.setFixedWidth(100)
        self.range_to = PlaceholderLineEdit("Range To")
        self.range_to.setFixedWidth(100)
        self.tick_size = PlaceholderLineEdit("Tick Size")
        self.tick_size.setFixedWidth(100)
        self.active_check = QCheckBox("Active")

        self.start_btn = QPushButton("Start")
        self.start_btn.setFixedWidth(130)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color:  royalblue;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #4169e1;
            }
        """)
        self.start_btn.clicked.connect(self.start_process)

        self.extra_range_frame.addWidget(self.range_from, 0, 0)
        self.extra_range_frame.addWidget(self.range_to, 0, 1)
        self.extra_range_frame.addWidget(self.tick_size, 0, 2)
        self.extra_range_frame.addWidget(self.active_check, 0, 3)
        self.extra_range_frame.addWidget(self.start_btn, 0, 4)

    def start_process(self):
        print("Start clicked")
        print(f"Range From: {self.range_from.text()}")
        print(f"Range To: {self.range_to.text()}")
        print(f"Tick Size: {self.tick_size.text()}")
        print(f"Active: {self.active_check.isChecked()}")

    def disable_strategy2_widgets(self):
        for i in range(self.combo_grid.count()):
            widget = self.combo_grid.itemAt(i).widget()
            if isinstance(widget, (QLineEdit, QComboBox)):
                widget.setDisabled(True)

    def reset_strategy1(self):
        self.ticker_combo.setCurrentIndex(0)
        self.expiry_combo.setCurrentIndex(0)
        for line_edit in [
            self.lot_entry, self.tick_entry,
            self.range_from_entry, self.range_to_entry
        ]:
            line_edit.setText("")
            line_edit.is_placeholder = True
            line_edit.setText(line_edit.placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    color: gray;
                    border: 1px solid #aaa;
                    border-radius: 6px;
                    padding: 6px;
                }
            """)
        self.active_checkbox.setChecked(True)

    def logout(self):
        # Update user_data.json to set logged_in to false
        with open('user_data.json', 'w') as f:
            json.dump({"logged_in": False}, f)
        
        # Import LoginWindow here to avoid circular import
        from login import LoginWindow
        WindowManager.get_instance().switch_to_window(LoginWindow)

    def show_change_password(self):
        from login import ChangePasswordWindow
        dialog = ChangePasswordWindow(self)
        dialog.exec_()

    def on_ticker_changed(self, ticker_text):
        self.expiry_combo.clear()
        self.expiry_combo.addItem("Select Expiry")
        self.lot_entry.setText("Lot Size")
        self.tick_entry.setText("Tick Price")
        
        if ticker_text == "Select Ticker":
            return
            
        symbol = self.symbol_map.get(ticker_text)
        exchange = self.symbol_exchange_map.get(symbol)
        
        if not exchange:
            QMessageBox.warning(self, "Error", f"No exchange found for symbol {symbol}")
            return

        try:
            # Request contract details to get available expiry months
            contract = Future(symbol=symbol, exchange=exchange, currency='USD')
            details = self.ib.reqContractDetails(contract)
            
            # Month number to name mapping
            month_names = {
                '01': 'January', '02': 'February', '03': 'March',
                '04': 'April', '05': 'May', '06': 'June',
                '07': 'July', '08': 'August', '09': 'September',
                '10': 'October', '11': 'November', '12': 'December'
            }
            
            # Extract and format expiry dates
            expiry_months = []
            for detail in details:
                contract_month = detail.contractMonth  # Format: YYYYMM
                if len(contract_month) == 6:
                    year = contract_month[:4]
                    month = contract_month[4:]
                    formatted_date = f"{year} {month_names.get(month, month)}"
                    expiry_months.append((contract_month, formatted_date))
            
            # Sort by original date and add formatted dates to combo box
            expiry_months.sort(key=lambda x: x[0])
            self.expiry_combo.addItems([date[1] for date in expiry_months])
            
            # Store original values for reference when selecting
            self.expiry_mapping = {date[1]: date[0] for date in expiry_months}
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch expiry months: {str(e)}")
    
    def on_expiry_changed(self, expiry):
        if expiry == "Select Expiry" or self.ticker_combo.currentText() == "Select Ticker":
            return
            
        symbol = self.symbol_map.get(self.ticker_combo.currentText())
        exchange = self.symbol_exchange_map.get(symbol)
        
        try:
            # Get the original date format from the mapping
            original_expiry = self.expiry_mapping.get(expiry, expiry)
            
            # Define the futures contract
            contract = Future(symbol=symbol, 
                            lastTradeDateOrContractMonth=original_expiry,
                            exchange=exchange, 
                            currency='USD')
            
            self.ib.qualifyContracts(contract)
            details = self.ib.reqContractDetails(contract)
            
            if not details:
                QMessageBox.warning(self, "Error", "Contract details not found.")
                return

            detail = details[0]
            
            # Update lot size and tick price
            self.lot_entry.setText(str(detail.minSize))
            self.tick_entry.setText(str(detail.minTick))
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch contract details: {str(e)}")
    
    def __del__(self):
        if hasattr(self, 'ib') and self.ib.isConnected():
            self.ib.disconnect()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TradingStrategyApp()
    window.show()
    sys.exit(app.exec_())