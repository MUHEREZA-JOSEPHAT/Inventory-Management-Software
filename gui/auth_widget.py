from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QStackedWidget, QMessageBox,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
from database import Database

class AuthWidget(QWidget):
    auth_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("5 STAR IMS - Welcome")
        # Remove fixed size for full-page look
        self.setMinimumSize(1200, 800)
        
        # Main layout (Horizontal: Left = Hero/Gradient, Right = Forms)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Side: Hero Section with Gradient
        self.hero_frame = QFrame()
        self.hero_frame.setObjectName("hero-frame")
        # Use stretch instead of fixed width
        hero_layout = QVBoxLayout(self.hero_frame)
        hero_layout.setContentsMargins(40, 40, 40, 40)
        
        logo_label = QLabel("5 ST★R\nSUPERMARKET")
        logo_label.setObjectName("hero-logo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(logo_label)
        
        hero_layout.addStretch()
        
        main_layout.addWidget(self.hero_frame, 1) # Stretch factor 1
        
        # Right Side: Form Section
        self.form_container = QStackedWidget()
        self.form_container.setObjectName("form-container")
        
        # Login Page
        self.login_page = self._create_login_page()
        self.form_container.addWidget(self.login_page)
        
        # Register Page
        self.register_page = self._create_register_page()
        self.form_container.addWidget(self.register_page)
        
        main_layout.addWidget(self.form_container, 1) # Stretch factor 1
        
        self._apply_styles()

    def _create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(20)
        
        title = QLabel("Sign In")
        title.setObjectName("form-title")
        layout.addWidget(title)
        
        subtitle = QLabel("Welcome back! Please enter your details.")
        subtitle.setObjectName("form-subtitle")
        layout.addWidget(subtitle)
        
        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("Username")
        layout.addWidget(self.login_user)
        
        self.login_pass = QLineEdit()
        self.login_pass.setPlaceholderText("Password")
        self.login_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.login_pass)
        
        login_btn = QPushButton("Access System")
        login_btn.setObjectName("primary-btn")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        switch_layout = QHBoxLayout()
        switch_text = QLabel("Don't have an account?")
        switch_text.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        switch_btn = QPushButton("Register Now")
        switch_btn.setObjectName("link-btn")
        switch_btn.clicked.connect(lambda: self.form_container.setCurrentIndex(1))
        switch_layout.addWidget(switch_text)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)
        
        layout.addStretch()
        return page

    def _create_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(15)
        
        title = QLabel("Registration")
        title.setObjectName("form-title")
        layout.addWidget(title)
        
        self.reg_full_name = QLineEdit()
        self.reg_full_name.setPlaceholderText("Full Name")
        layout.addWidget(self.reg_full_name)
        
        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("Username")
        layout.addWidget(self.reg_user)
        
        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Password")
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_pass)
        
        self.reg_confirm_pass = QLineEdit()
        self.reg_confirm_pass.setPlaceholderText("Confirm Password")
        self.reg_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_confirm_pass)
        
        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("primary-btn")
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)
        
        switch_btn = QPushButton("Already member? Sign In")
        switch_btn.setObjectName("link-btn")
        switch_btn.clicked.connect(lambda: self.form_container.setCurrentIndex(0))
        layout.addWidget(switch_btn)
        
        layout.addStretch()
        return page

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            #hero-frame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #0F2027, stop:0.5 #203A43, stop:1 #2C5364);
                border: none;
            }
            #hero-logo {
                background: transparent;
                font-size: 52px;
                font-weight: 900;
                color: white;
                margin-top: 180px;
                letter-spacing: 6px;
                text-shadow: 2px 2px 10px rgba(0,0,0,0.3);
            }
            #form-container {
                background-color: white;
            }
            #form-title {
                font-size: 36px;
                font-weight: 800;
                color: #1a1a1a;
                margin-bottom: 5px;
            }
            #form-subtitle {
                font-size: 15px;
                color: #7f8c8d;
                margin-bottom: 25px;
            }
            QLineEdit {
                padding: 16px;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
                background-color: #f8fafc;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #2575fc;
                background-color: white;
            }
            #primary-btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #2575fc, stop:1 #6a11cb);
                color: white;
                padding: 18px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 900;
                margin-top: 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            #primary-btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #1a5fdb, stop:1 #5a0ebf);
            }
            #link-btn {
                background: transparent;
                color: #2575fc;
                border: none;
                font-size: 14px;
                font-weight: 700;
                text-align: center;
                padding: 10px;
                margin-top: 10px;
            }
            #link-btn:hover {
                color: #1a5fdb;
                text-decoration: underline;
            }
        """)

    def handle_login(self):
        user = self.db.authenticate_user(self.login_user.text(), self.login_pass.text())
        if user:
            self.auth_success.emit({'id': user[0], 'username': user[1], 'full_name': user[2], 'role': user[3]})
        else:
            QMessageBox.critical(self, "Failed", "Invalid credentials.")

    def handle_register(self):
        if not all([self.reg_user.text(), self.reg_pass.text(), self.reg_full_name.text()]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        if self.reg_pass.text() != self.reg_confirm_pass.text():
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
            
        try:
            self.db.create_user(self.reg_user.text(), self.reg_pass.text(), self.reg_full_name.text())
            QMessageBox.information(self, "Success", "Registered! Proceed to login.")
            self.form_container.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
