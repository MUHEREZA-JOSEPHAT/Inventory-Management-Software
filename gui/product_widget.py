from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QLabel, QMessageBox,
    QComboBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from models.product import Product

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Add Product" if not product_data else "Edit Product")
        self.setMinimumWidth(400)
        self._save_btn = None
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
        
        # Add fields to form
        layout.addRow("Name:", self.name_edit)
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

    def _on_save_clicked(self):
        # Prevent accidental double-submits from rapid clicks
        if self._save_btn is not None:
            self._save_btn.setEnabled(False)
        self.accept()
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'price': self.price_spin.value(),
            'quantity': self.quantity_spin.value(),
            'reorder_point': self.reorder_spin.value(),
            'unit': self.unit_combo.currentText()
        }

class ProductWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.product = Product()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create header with title and add button
        header = QHBoxLayout()
        title = QLabel("Product Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Quantity", "Price", "Unit", "Reorder Point"
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
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        refresh_btn = QPushButton("Refresh")
        
        edit_btn.clicked.connect(self.edit_selected_product)
        delete_btn.clicked.connect(self.delete_selected_product)
        refresh_btn.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh the product table data"""
        products = self.product.get_all_products()
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product[2]} {product[5]}"))  # quantity with unit
            self.table.setItem(row, 3, QTableWidgetItem(f"${product[3]:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(product[5]))  # unit
            self.table.setItem(row, 5, QTableWidgetItem(str(product[4])))  # reorder point
    
    def add_product(self):
        """Show dialog to add a new product"""
        dialog = ProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.product.add_product(
                    data['name'],
                    data['quantity'],
                    data['price'],
                    data['reorder_point'],
                    data['unit']
                )
                self.refresh_data()
                self.window().show_success("Product added successfully!")
            except Exception as e:
                self.window().show_error(f"Error adding product: {str(e)}")
    
    def edit_product(self, index):
        """Edit the product at the given index"""
        row = index.row()
        product_id = int(self.table.item(row, 0).text())
        product_data = self.product.get_product(product_id)
        
        if product_data:
            dialog = ProductDialog(self, product_data)
            if dialog.exec():
                data = dialog.get_data()
                try:
                    self.product.update_product(
                        product_id,
                        name=data['name'],
                        quantity=data['quantity'],
                        price=data['price'],
                        reorder_point=data['reorder_point'],
                        unit=data['unit']
                    )
                    self.refresh_data()
                    self.window().show_success("Product updated successfully!")
                except Exception as e:
                    self.window().show_error(f"Error updating product: {str(e)}")
    
    def edit_selected_product(self):
        """Edit the currently selected product"""
        try:
            row = self.table.currentRow()
            if row < 0:
                self.window().show_warning("Please select a product to edit")
                return

            index = self.table.model().index(row, 0)
            self.edit_product(index)
        except Exception as e:
            self.window().show_error(f"Error opening edit dialog: {str(e)}")
    
    def delete_selected_product(self):
        """Delete the currently selected product"""
        selected = self.table.selectedItems()
        if not selected:
            self.window().show_warning("Please select a product to delete")
            return
        
        product_id = int(self.table.item(selected[0].row(), 0).text())
        product_name = self.table.item(selected[0].row(), 1).text()
        
        if self.window().show_confirmation(
            f"Are you sure you want to delete '{product_name}'?"
        ):
            try:
                if self.product.delete_product(product_id):
                    self.refresh_data()
                    self.window().show_success("Product deleted successfully!")
                else:
                    self.window().show_error("Failed to delete product")
            except Exception as e:
                self.window().show_error(f"Error deleting product: {str(e)}") 