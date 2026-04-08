from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QMessageBox,
    QFrame, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from .product_widget import ProductWidget
from .inventory_widget import InventoryWidget
from .sales_widget import SalesWidget
from .reports_widget import ReportsWidget
from .dashboard_widget import DashboardWidget
from .supplier_widget import SupplierWidget
from .chat_widget import ChatWidget

class NotificationWorker(QThread):
    finished = pyqtSignal(int)
    
    def __init__(self, comm_model):
        super().__init__()
        self.comm_model = comm_model
        
    def run(self):
        try:
            # Sync ALL incoming mail (this hits the server)
            self.comm_model.sync_incoming_emails()
            # Get the new count
            count = self.comm_model.get_total_unread_count()
            self.finished.emit(count)
        except Exception as e:
            print(f"Background Sync Error: {e}")
            self.finished.emit(-1)

class MainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        self.user_role = self.user_data.get('role', 'worker').lower()
        self.user_name = self.user_data.get('full_name', 'User')
        
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
        self.chat_widget = ChatWidget(current_user=self.user_name)
        
        # Communication Model for Global Notifications
        from models.supplier_communication import SupplierCommunication
        self.comm_model = SupplierCommunication()
        
        # Notification Worker
        self.notif_worker = NotificationWorker(self.comm_model)
        self.notif_worker.finished.connect(self._on_notif_finished)
        
        # Global Notification Timer (Check every 60 seconds for a snappier feel)
        self.notif_timer = QTimer(self)
        self.notif_timer.timeout.connect(self._check_global_notifications)
        self.notif_timer.start(60000) 
        
        QTimer.singleShot(1000, self._check_global_notifications) 
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.product_widget)
        self.stacked_widget.addWidget(self.inventory_widget)
        self.stacked_widget.addWidget(self.sales_widget)
        self.stacked_widget.addWidget(self.reports_widget)
        self.stacked_widget.addWidget(self.supplier_widget)
        self.stacked_widget.addWidget(self.chat_widget)
        
        # Set default page based on role
        if self.user_role == "admin":
            self._show_dashboard()
        else:
            self._show_products()
        
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
        if self.user_role == "admin":
            nav_buttons = [
                ("Dashboard", "🎯", self._show_dashboard),
                ("Products", "📦", self._show_products),
                ("Inventory", "📋", self._show_inventory),
                ("Sales", "🛍️", self._show_sales),
                ("Reports", "📊", self._show_reports),
                ("Suppliers", "🚚", self._show_suppliers),
                ("Support Chat", "💬", self._show_chat)
            ]
        else:
            nav_buttons = [
                ("Products", "📦", self._show_products),
                ("Inventory", "📋", self._show_inventory),
                ("Sales", "🛍️", self._show_sales)
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
        
        # Notification Bell
        self.bell_container = QWidget()
        self.bell_container.setFixedSize(50, 50) # Larger container for breathing room
        
        self.bell_btn = QPushButton("", self.bell_container)
        self.bell_btn.setObjectName("bell-btn")
        self.bell_btn.setFixedSize(40, 40)
        self.bell_btn.move(5, 5) # Centering inside container
        
        # Professional PNG Icon Replacement
        self.bell_btn.setIcon(QIcon("images/bell_notif.png"))
        self.bell_btn.setIconSize(QSize(22, 22))
        
        self.bell_btn.setStyleSheet("""
            QPushButton#bell-btn {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 20px;
                color: #1c2833;
            }
            QPushButton#bell-btn:hover {
                background-color: #f1f3f5;
                border: 1px solid #dee2e6;
            }
        """)
        self.bell_btn.clicked.connect(self._show_notif_dropdown)
        
        self.notif_badge = QLabel("0", self.bell_container)
        self.notif_badge.setFixedSize(18, 18)
        self.notif_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notif_badge.setStyleSheet("""
            background-color: #ff3b30;
            color: white;
            border-radius: 9px;
            font-size: 10px;
            font-weight: bold;
            border: 2px solid white;
        """)
        self.notif_badge.move(30, 2) # Positioned on the top-right corner
        self.notif_badge.hide()
        
        layout.addWidget(self.bell_container)
        layout.addSpacing(10)
        
        self.user_label = QLabel("Welcome, Admin")
        self.user_label.setObjectName("user-label")
        layout.addWidget(self.user_label)
        
        return header

    def _show_dashboard(self):
        """Show dashboard page"""
        self._update_nav_selection("Dashboard")
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.dashboard_widget.refresh_data()
    
    def _show_products(self):
        """Show products page"""
        self._update_nav_selection("Products")
        self.stacked_widget.setCurrentWidget(self.product_widget)
        self.product_widget.refresh_data()
    
    def _show_inventory(self):
        """Show inventory page"""
        self._update_nav_selection("Inventory")
        self.stacked_widget.setCurrentWidget(self.inventory_widget)
        self.inventory_widget.refresh_data()
    
    def _show_sales(self):
        """Show sales page"""
        self._update_nav_selection("Sales")
        self.stacked_widget.setCurrentWidget(self.sales_widget)
        self.sales_widget.refresh_data()
    
    def _show_reports(self):
        """Show reports page"""
        self._update_nav_selection("Reports")
        self.stacked_widget.setCurrentWidget(self.reports_widget)
        self.reports_widget.refresh_data()

    def _show_suppliers(self):
        """Show suppliers page"""
        self._update_nav_selection("Suppliers")
        self.stacked_widget.setCurrentWidget(self.supplier_widget)
        self.supplier_widget.refresh_data()

    def _show_notif_dropdown(self):
        """Displays a dropdown menu listing suppliers with unread messages"""
        summary = self.comm_model.get_unread_summary()
        
        if not summary:
            self.window().statusBar().showMessage("No new messages", 2000)
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px; }
            QMenu::item { padding: 8px 25px; border-radius: 4px; color: #1c2833; font-size: 13px; }
            QMenu::item:selected { background-color: #f4f6f8; color: #1a73e8; }
        """)
        
        for s in summary:
            action = menu.addAction(f"👤 {s['name']} ({s['count']})")
            action.triggered.connect(lambda checked, s=s: self._open_chat_directly(s))
            
        menu.addSeparator()
        view_all = menu.addAction("View All Suppliers")
        view_all.triggered.connect(self._show_suppliers)
        
        # Position menu below the bell
        menu.exec(self.bell_btn.mapToGlobal(self.bell_btn.rect().bottomLeft()))

    def _open_chat_directly(self, supplier_data):
        """Opens the communication dialog for a specific supplier and refreshes the badge"""
        from .supplier_email_dialog import SupplierEmailDialog
        
        dialog = SupplierEmailDialog(
            supplier_data['id'], 
            supplier_data['name'], 
            supplier_data['email'], 
            self
        )
        dialog.exec()
        
        # Immediately refresh unread count after closing/marking read
        self._check_global_notifications()

    def _check_global_notifications(self):
        """Triggers the background worker to check for NEW mail"""
        if not self.notif_worker.isRunning():
            self.notif_worker.start()

    def _on_notif_finished(self, unread_count):
        """Handles the result from the background sync thread"""
        if unread_count > 0:
            self.notif_badge.setText(str(unread_count))
            self.notif_badge.show()
        elif unread_count == 0:
            self.notif_badge.hide()
        # If unread_count is -1, it means a network error occurred - we stay silent

    def _show_chat(self):
        self._update_nav_selection("Support Chat")
        self.stacked_widget.setCurrentWidget(self.chat_widget)
        self.chat_widget.refresh_messages()

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

    def _update_nav_selection(self, page_name):
        for btn in self.nav_btns:
            btn.setChecked(page_name in btn.text())
    
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