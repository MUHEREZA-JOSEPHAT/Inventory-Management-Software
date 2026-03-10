from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QSpinBox, QLineEdit, QLabel, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from models.inventory import Inventory
from models.product import Product

class StockAdjustmentDialog(QDialog):
    def __init__(self, parent=None, product_id=None, product_name=None, current_quantity=0, unit='piece'):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle(f"Adjust Stock - {product_name}")
        self.setMinimumWidth(400)
        self.current_quantity = current_quantity
        self.unit = unit
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Show current quantity
        current_label = QLabel(f"Current Quantity: {self.current_quantity} {self.unit}")
        layout.addRow(current_label)
        
        # Create form fields
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(-999999, 999999)
        self.quantity_spin.setValue(0)
        
        self.reason_edit = QLineEdit()
        
        # Add fields to form
        layout.addRow("Quantity Change:", self.quantity_spin)
        layout.addRow("Reason:", self.reason_edit)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def get_data(self):
        return {
            'quantity_change': self.quantity_spin.value(),
            'reason': self.reason_edit.text().strip()
        }

class StockMovementDialog(QDialog):
    def __init__(self, parent=None, product_id=None, product_name=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle(f"Stock Movement History - {product_name}")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Date range selection
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        
        # Set default dates (last 30 days)
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-30))
        self.end_date.setDate(today)
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        date_layout.addWidget(refresh_btn)
        
        layout.addLayout(date_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Quantity Change", "Type"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the stock movement history"""
        movements = self.inventory.get_stock_movements(
            self.product_id,
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        )
        
        self.table.setRowCount(len(movements))
        for row, movement in enumerate(movements):
            self.table.setItem(row, 0, QTableWidgetItem(str(movement[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(movement[1])))
            self.table.setItem(row, 2, QTableWidgetItem(movement[2]))

class InventoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.inventory = Inventory()
        self.product = Product()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create header with title
        header = QHBoxLayout()
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Current Stock", "Reorder Point", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        adjust_btn = QPushButton("Adjust Stock")
        history_btn = QPushButton("View History")
        refresh_btn = QPushButton("Refresh")
        
        adjust_btn.clicked.connect(self.adjust_stock)
        history_btn.clicked.connect(self.view_history)
        refresh_btn.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(adjust_btn)
        button_layout.addWidget(history_btn)
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh the inventory table data"""
        products = self.product.get_all_products()
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # product fields are now in order:
            # [0] = product_id
            # [1] = name
            # [2] = quantity
            # [3] = price
            # [4] = reorder_point
            # [5] = unit
            # [6] = created_at
            
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))  # ID
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))       # Name
            
            # Convert quantity to integer for comparison
            quantity = int(product[2])  # quantity
            reorder_point = int(product[4])  # reorder_point
            
            # Display quantity with unit
            quantity_with_unit = f"{quantity} {product[5]}"  # quantity + unit
            self.table.setItem(row, 2, QTableWidgetItem(quantity_with_unit))
            
            self.table.setItem(row, 3, QTableWidgetItem(str(reorder_point)))
            
            # Set status based on quantity vs reorder point
            status = "Low Stock" if quantity <= reorder_point else "In Stock"
            status_item = QTableWidgetItem(status)
            if status == "Low Stock":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 4, status_item)
    
    def get_selected_product(self):
        """Get the currently selected product info"""
        selected = self.table.selectedItems()
        if not selected:
            self.window().show_warning("Please select a product")
            return None
        
        row = selected[0].row()
        return {
            'id': int(self.table.item(row, 0).text()),
            'name': self.table.item(row, 1).text(),
            'quantity': int(self.table.item(row, 2).text().split()[0]),
            'unit': self.table.item(row, 2).text().split()[1]
        }
    
    def adjust_stock(self):
        """Show dialog to adjust stock level"""
        product = self.get_selected_product()
        if not product:
            return
        
        dialog = StockAdjustmentDialog(
            self, 
            product['id'], 
            product['name'],
            product['quantity'],
            product['unit']
        )
        if dialog.exec():
            data = dialog.get_data()
            try:
                if self.product.update_quantity(
                    product['id'],
                    data['quantity_change']
                ):
                    self.refresh_data()
                    self.window().show_success("Stock level updated successfully!")
                else:
                    self.window().show_error("Failed to update stock level")
            except Exception as e:
                self.window().show_error(f"Error updating stock level: {str(e)}")
    
    def view_history(self):
        """Show stock movement history dialog"""
        product = self.get_selected_product()
        if not product:
            return
        
        dialog = StockMovementDialog(self, product['id'], product['name'])
        dialog.exec() 