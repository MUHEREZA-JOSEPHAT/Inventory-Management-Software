from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QMessageBox,
    QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from .product_widget import ProductWidget
from .inventory_widget import InventoryWidget
from .sales_widget import SalesWidget
from .reports_widget import ReportsWidget
from .dashboard_widget import DashboardWidget
from .supplier_widget import SupplierWidget
from .chat_widget import ChatWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        central_widget.setObjectName("central-widget")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right side container (Header + Content)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header bar (Inspired by reference images)
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_container)
        
        # Add pages to stacked widget
        self.dashboard_widget = DashboardWidget()
        self.product_widget = ProductWidget()
        self.inventory_widget = InventoryWidget()
        self.sales_widget = SalesWidget()
        self.reports_widget = ReportsWidget()
        self.supplier_widget = SupplierWidget()
        self.chat_widget = ChatWidget(current_user="Admin")
        
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.product_widget)
        self.stacked_widget.addWidget(self.inventory_widget)
        self.stacked_widget.addWidget(self.sales_widget)
        self.stacked_widget.addWidget(self.reports_widget)
        self.stacked_widget.addWidget(self.supplier_widget)
        self.stacked_widget.addWidget(self.chat_widget)
        
        # Set default page
        self._show_dashboard()
        
        # Set stylesheet
        self._apply_stylesheet()
        
    def _create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 40, 20, 40)
        layout.setSpacing(15)
        
        # Add title
        title = QLabel("5 ST★R")
        title.setObjectName("sidebar-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #34495e; margin: 10px 0px 20px 0px;")
        layout.addWidget(line)
        
        # Add navigation buttons
        nav_buttons = [
            ("Dashboard", "🎯", self._show_dashboard),
            ("Products", "📦", self._show_products),
            ("Inventory", "📋", self._show_inventory),
            ("Sales", "🛍️", self._show_sales),
            ("Reports", "📊", self._show_reports),
            ("Suppliers", "🚚", self._show_suppliers),
            ("Support Chat", "💬", self._show_chat)
        ]
        
        self.nav_btns = []
        for text, icon, callback in nav_buttons:
            btn = QPushButton(f" {icon}  {text}")
            btn.setObjectName("nav-button")
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            self.nav_btns.append(btn)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton(" Logout")
        logout_btn.setObjectName("logout-button")
        logout_btn.clicked.connect(self.close)
        layout.addWidget(logout_btn)
        
        return sidebar
        
    def _create_header(self):
        """Create the top header bar"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Search area (Functional QLineEdit)
        search_box = QFrame()
        search_box.setObjectName("search-box")
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(15, 0, 15, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search for products or categories...")
        self.search_input.setFrame(False)
        self.search_input.setStyleSheet("background: transparent; color: #1c2833; font-size: 13px; min-height: 40px;")
        self.search_input.textChanged.connect(self._on_search_changed)
        
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_box)
        
        layout.addStretch()
        
        # User Profile area
        self.user_label = QLabel("Welcome, Admin")
        self.user_label.setObjectName("user-label")
        layout.addWidget(self.user_label)
        
        return header
        
    def _show_dashboard(self):
        """Show dashboard page"""
        self._update_nav_selection(0)
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.dashboard_widget.refresh_data()
    
    def _show_products(self):
        """Show products page"""
        self._update_nav_selection(1)
        self.stacked_widget.setCurrentWidget(self.product_widget)
        self.product_widget.refresh_data()
    
    def _show_inventory(self):
        """Show inventory page"""
        self._update_nav_selection(2)
        self.stacked_widget.setCurrentWidget(self.inventory_widget)
        self.inventory_widget.refresh_data()
    
    def _show_sales(self):
        """Show sales page"""
        self._update_nav_selection(3)
        self.stacked_widget.setCurrentWidget(self.sales_widget)
        self.sales_widget.refresh_data()
    
    def _show_reports(self):
        """Show reports page"""
        self._update_nav_selection(4)
        self.stacked_widget.setCurrentWidget(self.reports_widget)
        self.reports_widget.refresh_data()

    def _show_suppliers(self):
        """Show suppliers page"""
        self._update_nav_selection(5)
        self.stacked_widget.setCurrentWidget(self.supplier_widget)
        self.supplier_widget.refresh_data()

    def _show_chat(self):
        self._update_nav_selection(6)
        self.stacked_widget.setCurrentWidget(self.chat_widget)
        self.chat_widget.refresh_data()

    def _on_search_changed(self, text):
        """Global search handler"""
        # Switch to products tab if not on a searchable tab
        current = self.stacked_widget.currentWidget()
        if current not in [self.product_widget, self.inventory_widget, self.sales_widget]:
            self._show_products()
        
        # Filter all relevant modules
        self.product_widget.filter_data(text)
        self.inventory_widget.filter_data(text)
        if hasattr(self.sales_widget, 'filter_data'):
            self.sales_widget.filter_data(text)

    def _update_nav_selection(self, index):
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fc;
            }
            
            #sidebar {
                background-color: #1c2833;
                border: none;
            }
            
            #sidebar-title {
                color: #ffffff;
                font-size: 32px;
                font-weight: 900;
                padding: 10px;
                letter-spacing: 2px;
            }
            
            #nav-button {
                background-color: transparent;
                color: #abb2b9;
                border: none;
                padding: 15px 25px;
                text-align: left;
                font-size: 15px;
                border-radius: 8px;
                font-weight: 600;
            }
            
            #nav-button:hover {
                background-color: #2c3e50;
                color: #ffffff;
            }
            
            #nav-button:checked {
                background-color: #2575fc;
                color: #ffffff;
            }
            
            #logout-button {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 20px;
            }
            
            #header {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
            
            #user-label {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            
            #search-box {
                background-color: #f2f4f7;
                border-radius: 20px;
                min-width: 300px;
            }

            QWidget#central-widget {
                background-color: #f7f9fc;
            }
            
            QPushButton {
                background-color: #2575fc;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton:hover {
                background-color: #1a5fdb;
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f8f9fa;
            }
            
            QHeaderView::section {
                background-color: #ffffff;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #f1f3f5;
                font-weight: bold;
                color: #34495e;
            }
        """)
    
    def show_error(self, message):
        """Show error message dialog"""
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message):
        """Show success message dialog"""
        QMessageBox.information(self, "Success", message)
    
    def show_warning(self, message):
        """Show warning message dialog"""
        QMessageBox.warning(self, "Warning", message)
    
    def show_confirmation(self, message):
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self, "Confirmation", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes 