from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QLabel, QMessageBox,
    QComboBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from models.product import Product
from models.category import Category
from .category_widget import CategoryWidget

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Add Product" if not product_data else "Edit Product")
        self.setMinimumWidth(400)
        self._save_btn = None
        self.category_model = Category()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Create form fields
        self.name_edit = QLineEdit()
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$")
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 999999)
        self.quantity_spin.setValue(0)
        
        self.reorder_spin = QSpinBox()
        self.reorder_spin.setRange(0, 999999)
        
        # Add unit selection
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            'piece', 'kg', 'g', 'lb', 'oz', 'liter', 'ml', 'box', 'pack',
            'dozen', 'pair', 'set', 'roll', 'meter', 'yard', 'foot'
        ])
        
        self.category_combo = QComboBox()
        self._load_categories()
        
        # Add fields to form
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Category:", self.category_combo)
        layout.addRow("Price:", self.price_spin)
        layout.addRow("Quantity:", self.quantity_spin)
        layout.addRow("Unit:", self.unit_combo)
        layout.addRow("Reorder Point:", self.reorder_spin)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        self._save_btn = save_btn
        save_btn.clicked.connect(self._on_save_clicked)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
        
        # If editing, populate fields
        if self.product_data:
            self.name_edit.setText(self.product_data[1])
            self.price_spin.setValue(self.product_data[3])
            self.quantity_spin.setValue(self.product_data[2])
            self.reorder_spin.setValue(self.product_data[4])
            if len(self.product_data) > 5:  # Check if unit exists in data
                index = self.unit_combo.findText(self.product_data[5])
                if index >= 0:
                    self.unit_combo.setCurrentIndex(index)
            
            # Set category
            category_id = self.product_data[6] if len(self.product_data) > 6 else None
            if category_id:
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == category_id:
                        self.category_combo.setCurrentIndex(i)
                        break

    def _load_categories(self):
        self.category_combo.clear()
        self.category_combo.addItem("None", None)
        categories = self.category_model.get_all_categories()
        for cat in categories:
            self.category_combo.addItem(cat[1], cat[0])

    def _on_save_clicked(self):
        # Prevent accidental double-submits from rapid clicks
        if self._save_btn is not None:
            self._save_btn.setEnabled(False)
        self.accept()

class ProductWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.product = Product()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Create header with title and add button
        header = QHBoxLayout()
        title = QLabel("5 ST★R Products")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #1c2833;")
        
        add_btn = QPushButton(" ➕ Add New Product")
        add_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        add_btn.clicked.connect(self.add_product)
        
        cat_btn = QPushButton(" 📂 Categories")
        cat_btn.setStyleSheet("background-color: #2575fc; color: white;")
        cat_btn.clicked.connect(self.manage_categories)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(cat_btn)
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # ID, Name, Category, Quantity, Price, Unit, Reorder
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "Quantity", "Price", "Unit", "Reorder Point"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_product)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, header.ResizeMode.ResizeToContents)
        
        self.table.setColumnHidden(0, True) # Hide ID column
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Add action buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Product")
        delete_btn = QPushButton("Delete Product")
        refresh_btn = QPushButton("Refresh")
        
        edit_btn.clicked.connect(self.handle_edit_clicked)
        delete_btn.clicked.connect(self.delete_product)
        refresh_btn.clicked.connect(self.refresh_data)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)

    def refresh_data(self):
        """Refresh product table data"""
        products = self.product.get_all_products()
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            # product fields: [0]ID, [1]Name, [2]Qty, [3]Price, [4]Reorder, [5]Unit, [6]CreatedAt, [7]Category
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QTableWidgetItem(product[7] if product[7] else "None"))
            self.table.setItem(row, 3, QTableWidgetItem(str(product[2])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${product[3]:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(product[5]))
            self.table.setItem(row, 6, QTableWidgetItem(str(product[4])))

    def filter_data(self, search_term):
        """Filter table rows based on search term (Name or Category)"""
        search_term = search_term.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1) # Name
            cat_item = self.table.item(row, 2)  # Category
            
            match = not search_term # Show all if search is empty
            if not match:
                if name_item and search_term in name_item.text().lower():
                    match = True
                elif cat_item and search_term in cat_item.text().lower():
                    match = True
                    
            self.table.setRowHidden(row, not match)

    def manage_categories(self):
        """Show Category management dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Categories")
        dialog.setMinimumSize(800, 500)
        layout = QVBoxLayout(dialog)
        
        cat_widget = CategoryWidget()
        layout.addWidget(cat_widget)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        self.refresh_data() # Refresh in case categories changed
    
    def add_product(self):
        """Show dialog to add a new product"""
        dialog = ProductDialog(self)
        if dialog.exec():
            # Get data from dialog
            name = dialog.name_edit.text().strip()
            price = dialog.price_spin.value()
            quantity = dialog.quantity_spin.value()
            reorder = dialog.reorder_spin.value()
            unit = dialog.unit_combo.currentText()
            cat_id = dialog.category_combo.currentData()
            
            if name:
                if self.product.add_product(name, quantity, price, reorder, unit, cat_id):
                    self.refresh_data()
                    self.window().show_success(f"Product '{name}' added!")
                else:
                    self.window().show_error("Failed to add product")
            else:
                self.window().show_warning("Product name is required")

    def handle_edit_clicked(self):
        """Handle edit button click"""
        selected = self.table.selectedItems()
        if selected:
            self.edit_product(self.table.indexFromItem(selected[0]))
        else:
            self.window().show_warning("Please select a product to edit")

    def edit_product(self, index):
        """Show dialog to edit an existing product"""
        row = index.row()
        product_id = int(self.table.item(row, 0).text())
        
        # Get full product details
        product_data = self.product.get_product(product_id)
        if not product_data:
            return
            
        dialog = ProductDialog(self, product_data)
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            price = dialog.price_spin.value()
            quantity = dialog.quantity_spin.value()
            reorder = dialog.reorder_spin.value()
            unit = dialog.unit_combo.currentText()
            cat_id = dialog.category_combo.currentData()
            
            if self.product.update_product(product_id, name, price, reorder, unit, quantity, cat_id):
                self.refresh_data()
                self.window().show_success("Product updated!")
            else:
                self.window().show_error("Failed to update product")

    def delete_product(self):
        """Delete selected product"""
        selected = self.table.selectedItems()
        if not selected:
            self.window().show_warning("Please select a product to delete")
            return
            
        row = selected[0].row()
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 1).text()
        
        if self.window().show_confirmation(f"Are you sure you want to delete '{product_name}'?"):
            if self.product.delete_product(product_id):
                self.refresh_data()
                self.window().show_success("Product deleted successfully!")
            else:
                self.window().show_error("Failed to delete product")