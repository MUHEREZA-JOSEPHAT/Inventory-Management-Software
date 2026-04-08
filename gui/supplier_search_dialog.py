from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from models.supplier import Supplier

class SupplierSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.supplier_model = Supplier()
        self.selected_supplier = None
        
        self.setWindowTitle("Select Supplier for Bulk Order")
        self.setMinimumSize(400, 500)
        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("🔍 Select a Supplier")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2ecc71;")
        layout.addWidget(title)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or email...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
            }
        """)
        self.search_input.textChanged.connect(self.filter_suppliers)
        layout.addWidget(self.search_input)

        # Results List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e8f5e9;
                color: #2e7d32;
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Confirm Selection")
        self.select_btn.setStyleSheet("background: #2ecc71; color: white; padding: 12px; font-weight: bold; border-radius: 6px;")
        self.select_btn.clicked.connect(self.accept_selection)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #f8f9fa; color: #333; padding: 12px; border-radius: 6px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_suppliers(self):
        self.suppliers = self.supplier_model.get_all_suppliers()
        self.populate_list(self.suppliers)

    def populate_list(self, suppliers):
        self.list_widget.clear()
        for s in suppliers:
            # s = (id, name, contact_person, phone, email, address)
            item = QListWidgetItem(f"🏢 {s[1]}\n📧 {s[4]}")
            item.setData(Qt.ItemDataRole.UserRole, (s[0], s[1], s[4]))
            self.list_widget.addItem(item)

    def filter_suppliers(self, text):
        filtered = [s for s in self.suppliers if text.lower() in s[1].lower() or text.lower() in s[2].lower()]
        self.populate_list(filtered)

    def accept_selection(self):
        current = self.list_widget.currentItem()
        if current:
            self.selected_supplier = current.data(Qt.ItemDataRole.UserRole)
            self.accept()
