from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame,
    QHBoxLayout, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import sys
import os
import json
from window_manager import WindowManager

CREDENTIALS_FILE = "user_data.json"

def is_logged_in():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
            return data.get("logged_in", False)
    return False

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading System Login")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e3e6;
                border-radius: 5px;
                background-color: white;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #2d5ca6;
            }
            QPushButton {
                background-color: #2d5ca6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1e3d70;
            }
            QLabel {
                color: #333;
                font-size: 12px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(main_layout)

        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "icons", "raru.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Trading System")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d5ca6; margin-bottom: 20px;")
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        main_layout.addLayout(logo_layout)

        main_layout.addSpacing(30)

        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout()
        form_container.setLayout(form_layout)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Log In")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.login_button.setFixedHeight(40)

        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(15)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(25)
        form_layout.addWidget(self.login_button)

        forgot_password_label = QLabel('<a href="#">Forgot Password?</a>')
        forgot_password_label.setAlignment(Qt.AlignRight)
        forgot_password_label.setTextFormat(Qt.RichText)
        forgot_password_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        forgot_password_label.setOpenExternalLinks(False)
        forgot_password_label.setStyleSheet("QLabel { color: #2d5ca6; font-size: 11px; } QLabel:hover { color: #1e3d70; }")
        forgot_password_label.linkActivated.connect(self.forgot_password)

        form_layout.addSpacing(10)
        form_layout.addWidget(forgot_password_label)

        main_layout.addWidget(form_container)
        main_layout.addStretch()

        qr = self.frameGeometry()
        cp = QApplication.desktop().screen().rect().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump({"logged_in": True}, f)

            from file_handler import TradingStrategyApp
            WindowManager.get_instance().switch_to_window(TradingStrategyApp)
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password!")

    def forgot_password(self):
        username = self.username_input.text().strip()

        if username.lower() == "admin":
            QMessageBox.information(self, "Password Recovery", "Your password is: admin")
        else:
            QMessageBox.information(
                self,
                "Password Reset",
                "Username not found or password reset instructions sent to your email (simulated)."
            )

class ChangePasswordWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #2d5ca6;
            }
        """)
        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Title
        title_label = QLabel("Change Password")
        title_label.setStyleSheet("""
            QLabel {
                color: #2d5ca6;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(20)

        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        form_container.setLayout(form_layout)

        # Password fields
        current_pass_label = QLabel("Current Password:")
        current_pass_label.setStyleSheet("font-weight: bold;")
        self.old_password = QLineEdit()
        self.old_password.setPlaceholderText("Enter your current password")
        self.old_password.setEchoMode(QLineEdit.Password)

        new_pass_label = QLabel("New Password:")
        new_pass_label.setStyleSheet("font-weight: bold;")
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Enter new password")
        self.new_password.setEchoMode(QLineEdit.Password)

        confirm_pass_label = QLabel("Confirm New Password:")
        confirm_pass_label.setStyleSheet("font-weight: bold;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm your new password")
        self.confirm_password.setEchoMode(QLineEdit.Password)

        # Add fields to form layout
        form_layout.addWidget(current_pass_label)
        form_layout.addWidget(self.old_password)
        form_layout.addSpacing(10)
        form_layout.addWidget(new_pass_label)
        form_layout.addWidget(self.new_password)
        form_layout.addSpacing(10)
        form_layout.addWidget(confirm_pass_label)
        form_layout.addWidget(self.confirm_password)
        form_layout.addSpacing(20)

        # Update button
        update_button = QPushButton("UPDATE PASSWORD")
        update_button.setCursor(Qt.PointingHandCursor)
        update_button.setFixedHeight(45)
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #2d5ca6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1e3d70;
            }
        """)
        update_button.clicked.connect(self.update_password)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(update_button)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)

        layout.addWidget(form_container)
        layout.addStretch()

    def update_password(self):
        old_password = self.old_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()

        if old_password != "admin":
            QMessageBox.warning(self, "Error", "Current password is incorrect!")
            return

        if not new_password:
            QMessageBox.warning(self, "Error", "New password cannot be empty!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match!")
            return

        # Here you would typically update the password in your database
        # For now, we'll just show a success message
        QMessageBox.information(self, "Success", "Password has been updated successfully!")
        self.accept()

    def center_on_screen(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    if is_logged_in():
        from file_handler import TradingStrategyApp
        window = WindowManager.get_instance().switch_to_window(TradingStrategyApp)
    else:
        window = WindowManager.get_instance().switch_to_window(LoginWindow)

    sys.exit(app.exec_())
