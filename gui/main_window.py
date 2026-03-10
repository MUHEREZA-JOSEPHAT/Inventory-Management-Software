from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from .product_widget import ProductWidget
from .inventory_widget import InventoryWidget
from .sales_widget import SalesWidget
from .reports_widget import ReportsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Add pages to stacked widget
        self.product_widget = ProductWidget()
        self.inventory_widget = InventoryWidget()
        self.sales_widget = SalesWidget()
        self.reports_widget = ReportsWidget()
        
        self.stacked_widget.addWidget(self.product_widget)
        self.stacked_widget.addWidget(self.inventory_widget)
        self.stacked_widget.addWidget(self.sales_widget)
        self.stacked_widget.addWidget(self.reports_widget)
        
        # Set stylesheet
        self._apply_stylesheet()
        
    def _create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # Add title
        title = QLabel("IMS")
        title.setObjectName("sidebar-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add navigation buttons
        nav_buttons = [
            ("Products", self._show_products),
            ("Inventory", self._show_inventory),
            ("Sales", self._show_sales),
            ("Reports", self._show_reports)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName("nav-button")
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        return sidebar
    
    def _show_products(self):
        """Show products page"""
        self.stacked_widget.setCurrentWidget(self.product_widget)
        self.product_widget.refresh_data()
    
    def _show_inventory(self):
        """Show inventory page"""
        self.stacked_widget.setCurrentWidget(self.inventory_widget)
        self.inventory_widget.refresh_data()
    
    def _show_sales(self):
        """Show sales page"""
        self.stacked_widget.setCurrentWidget(self.sales_widget)
        self.sales_widget.refresh_data()
    
    def _show_reports(self):
        """Show reports page"""
        self.stacked_widget.setCurrentWidget(self.reports_widget)
        self.reports_widget.refresh_data()
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            #sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            
            #sidebar-title {
                color: #ecf0f1;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
            
            #nav-button {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                border-radius: 5px;
            }
            
            #nav-button:hover {
                background-color: #34495e;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #2472a4;
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: bold;
            }
            
            QMessageBox {
                background-color: white;
            }
            
            QMessageBox QPushButton {
                min-width: 80px;
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