from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QLabel, QMessageBox, QAbstractItemView,
    QComboBox, QSpinBox, QDoubleSpinBox, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from models.supplier import Supplier
from models.product import Product
from models.order import Order
from models.category import Category

class OrderSuppliesDialog(QDialog):
    """Popup to place a new supply order with support for new product entry"""
    def __init__(self, parent=None, selected_supplier_id=None):
        super().__init__(parent)
        self.setWindowTitle("Order Supplies")
        self.setMinimumSize(900, 650)
        
        self.supplier_model = Supplier()
        self.product_model = Product()
        self.order_model = Order()
        self.category_model = Category()
        self.cart_items = [] # List of {product_id, name, qty, price, total, is_new, cat_id, unit}
        
        self.setup_ui(selected_supplier_id)
        
    def setup_ui(self, selected_supplier_id):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Supplier Selection
        supp_layout = QHBoxLayout()
        supp_layout.addWidget(QLabel("Select Supplier:"))
        self.supplier_combo = QComboBox()
        suppliers = self.supplier_model.get_all_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s[1], s[0])
        
        if selected_supplier_id:
            index = self.supplier_combo.findData(selected_supplier_id)
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)
        
        supp_layout.addWidget(self.supplier_combo, 1)
        layout.addLayout(supp_layout)
        
        # --- Product Entry Area ---
        prod_box = QFrame()
        prod_box.setFrameShape(QFrame.Shape.StyledPanel)
        prod_box.setStyleSheet("QFrame { border: 1px solid #dcdde1; border-radius: 5px; background: #f8f9fa; } QLabel { border: none; }")
        prod_v_layout = QVBoxLayout(prod_box)
        
        # Top row: Search/Select
        top_row = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.product_combo.setPlaceholderText("Select product OR type NEW name...")
        
        products = self.product_model.get_all_products(include_ordered=True)
        self.product_combo.addItem("", None) # Empty start
        for p in products:
            self.product_combo.addItem(f"{p[1]} (Stock: {p[2]} {p[5]})", (p[0], p[1], p[3], p[5], p[7]))
        
        self.product_combo.currentIndexChanged.connect(self._on_product_selected)
        self.product_combo.editTextChanged.connect(self._on_product_text_changed)
        
        top_row.addWidget(QLabel("Product:"), 0)
        top_row.addWidget(self.product_combo, 3)
        prod_v_layout.addLayout(top_row)
        
        # New Product Details (Hidden by default)
        self.new_prod_frame = QFrame()
        self.new_prod_frame.setVisible(False)
        new_prod_layout = QHBoxLayout(self.new_prod_frame)
        new_prod_layout.setContentsMargins(0, 0, 0, 0)
        
        self.new_cat_combo = QComboBox()
        cats = self.category_model.get_all_categories()
        for c in cats:
            self.new_cat_combo.addItem(c[1], c[0])
            
        self.new_unit_combo = QComboBox()
        self.new_unit_combo.addItems(['piece', 'kg', 'g', 'liter', 'ml', 'box', 'pack'])
        
        new_prod_layout.addWidget(QLabel("New Product Category:"), 0)
        new_prod_layout.addWidget(self.new_cat_combo, 1)
        new_prod_layout.addWidget(QLabel("Unit:"), 0)
        new_prod_layout.addWidget(self.new_unit_combo, 1)
        prod_v_layout.addWidget(self.new_prod_frame)
        
        # Qty and Price
        bottom_row = QHBoxLayout()
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 99999)
        self.qty_spin.setValue(1)
        
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999)
        self.price_spin.setPrefix("$")
        
        add_btn = QPushButton("Add to Order List")
        add_btn.setStyleSheet("background-color: #2575fc; color: white; padding: 10px; font-weight: bold;")
        add_btn.clicked.connect(self._add_to_cart)
        
        bottom_row.addWidget(QLabel("Quantity:"), 0)
        bottom_row.addWidget(self.qty_spin, 1)
        bottom_row.addWidget(QLabel("Cost Price (Unit):"), 0)
        bottom_row.addWidget(self.price_spin, 1)
        bottom_row.addWidget(add_btn, 2)
        prod_v_layout.addLayout(bottom_row)
        
        layout.addWidget(prod_box)
        
        # Cart Table
        self.table = QTableWidget()
        self.table.setColumnCount(6) # ID, Product, Type, Qty, Price, Total
        self.table.setHorizontalHeaderLabels(["ID", "Product Name", "Type", "Quantity", "Unit Price", "Total"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in [2, 3, 4, 5]: h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Footer
        footer = QHBoxLayout()
        self.summary_label = QLabel("Items: 0 | Grand Total: $0.00")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2ecc71;")
        
        self.place_order_btn = QPushButton("🚀 Place Bulk Order")
        self.place_order_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 12px 30px; font-weight: bold; border-radius: 5px;")
        self.place_order_btn.clicked.connect(self._place_order)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        footer.addWidget(self.summary_label)
        footer.addStretch()
        footer.addWidget(self.place_order_btn)
        footer.addWidget(cancel_btn)
        layout.addLayout(footer)

    def _on_product_selected(self, index):
        data = self.product_combo.currentData()
        if data:
            # Existing product
            self.new_prod_frame.setVisible(False)
            self.price_spin.setValue(data[2]) # Default to current selling price as a starting point for cost
        else:
            # Text might have matched nothing
            pass

    def _on_product_text_changed(self, text):
        # If the text in the combo doesn't match any item exactly, it's potentially a new product
        is_existing = False
        for i in range(self.product_combo.count()):
            if self.product_combo.itemText(i) == text:
                is_existing = True
                break
        
        if not is_existing and text.strip():
            self.new_prod_frame.setVisible(True)
        else:
            # Check if it matches an existing product data
            if self.product_combo.currentData():
                self.new_prod_frame.setVisible(False)

    def _add_to_cart(self):
        text = self.product_combo.currentText().strip()
        if not text:
            return
            
        data = self.product_combo.currentData()
        qty = self.qty_spin.value()
        price = self.price_spin.value()
        
        if data:
            # Existing product
            self.cart_items.append({
                'product_id': data[0],
                'name': data[1],
                'qty': qty,
                'price': price,
                'total': qty * price,
                'is_new': False
            })
        else:
            # New product
            cat_id = self.new_cat_combo.currentData()
            unit = self.new_unit_combo.currentText()
            self.cart_items.append({
                'product_id': None,
                'name': text,
                'qty': qty,
                'price': price,
                'total': qty * price,
                'is_new': True,
                'cat_id': cat_id,
                'unit': unit
            })
            
        self._refresh_table()
        # Reset entry area
        self.product_combo.setCurrentIndex(0)
        self.qty_spin.setValue(1)
        self.price_spin.setValue(0)

    def _refresh_table(self):
        self.table.setRowCount(len(self.cart_items))
        total_price = 0
        for row, item in enumerate(self.cart_items):
            type_text = "✨ New Product" if item['is_new'] else "Existing"
            self.table.setItem(row, 0, QTableWidgetItem(str(item['product_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.table.setItem(row, 2, QTableWidgetItem(type_text))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${item['price']:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${item['total']:,.2f}"))
            total_price += item['total']
            
        self.summary_label.setText(f"Items: {len(self.cart_items)} | Grand Total: ${total_price:,.2f}")

    def _place_order(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Warning", "Cart is empty")
            return
            
        supplier_id = self.supplier_combo.currentData()
        success_count = 0
        
        for item in self.cart_items:
            product_id = item['product_id']
            if item['is_new']:
                # Create the product first as 'Ordered'
                product_id = self.product_model.add_product(
                    item['name'], 0, item['price'], 0, item['unit'], item['cat_id'], status='Ordered'
                )
                if not product_id:
                    continue
            
            if self.order_model.place_order(supplier_id, product_id, item['qty'], item['price']):
                success_count += 1
                
        if success_count == len(self.cart_items):
            QMessageBox.information(self, "Success", "All orders placed successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Partial Success", f"{success_count}/{len(self.cart_items)} items processed.")

class OrderHistoryDialog(QDialog):
    """View all past supply orders"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supply Order History")
        self.setMinimumSize(1000, 600)
        self.order_model = Order()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Order ID", "Supplier", "Product", "Quantity", "Unit Cost", "Total", "Status", "Order Date"
        ])
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for i in [3, 4, 5, 6, 7]: h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.refresh_data()

    def refresh_data(self):
        orders = self.order_model.get_all_orders()
        self.table.setRowCount(len(orders))
        for row, o in enumerate(orders):
            # [0]id, [1]supp, [2]prod, [3]qty, [4]price, [5]total, [6]status, [7]date
            self.table.setItem(row, 0, QTableWidgetItem(str(o[0])))
            self.table.setItem(row, 1, QTableWidgetItem(o[1]))
            self.table.setItem(row, 2, QTableWidgetItem(o[2]))
            self.table.setItem(row, 3, QTableWidgetItem(str(o[3])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${o[4]:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${o[5]:,.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(o[6]))
            self.table.setItem(row, 7, QTableWidgetItem(str(o[7])))

class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.setWindowTitle("Add Supplier" if not supplier_data else "Edit Supplier")
        self.setMinimumWidth(450)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        
        self.name_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        
        layout.addRow("🏢 Business Name:", self.name_edit)
        layout.addRow("👤 Contact Person:", self.contact_edit)
        layout.addRow("📞 Phone Number:", self.phone_edit)
        layout.addRow("📧 Email Address:", self.email_edit)
        layout.addRow("📍 Business Address:", self.address_edit)
        
        if self.supplier_data:
            self.name_edit.setText(self.supplier_data[1])
            self.contact_edit.setText(self.supplier_data[2])
            self.phone_edit.setText(self.supplier_data[3])
            self.email_edit.setText(self.supplier_data[4])
            self.address_edit.setText(self.supplier_data[5])
            
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Details")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px; font-weight: bold;")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
        
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'contact_person': self.contact_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'address': self.address_edit.text().strip()
        }

class SupplierWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.supplier = Supplier()
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with multiple actions
        header = QHBoxLayout()
        title = QLabel("5 ST★R Suppliers")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #1c2833;")
        
        order_supplies_btn = QPushButton(" 📦 Order Supplies")
        order_supplies_btn.setStyleSheet("background-color: #2575fc; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        
        orders_btn = QPushButton(" 🕒 Orders History")
        orders_btn.setStyleSheet("background-color: #34495e; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        
        add_btn = QPushButton(" ➕ Add Supplier")
        add_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        
        order_supplies_btn.clicked.connect(self.order_supplies)
        orders_btn.clicked.connect(self.view_orders)
        add_btn.clicked.connect(self.add_supplier)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(order_supplies_btn)
        header.addWidget(orders_btn)
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Contact", "Phone", "Email", "Address"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_selected_supplier)
        
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(1, header_view.ResizeMode.Stretch)
        
        self.table.setColumnHidden(0, True) # Hide ID column
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        
        edit_btn.clicked.connect(self.edit_selected_supplier)
        delete_btn.clicked.connect(self.delete_selected_supplier)
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def refresh_data(self):
        suppliers = self.supplier.get_all_suppliers()
        self.table.setRowCount(len(suppliers))
        for row, s in enumerate(suppliers):
            for col, val in enumerate(s[:6]):
                self.table.setItem(row, col, QTableWidgetItem(str(val)))
                
    def add_supplier(self):
        dialog = SupplierDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.supplier.add_supplier(**data)
                self.refresh_data()
                self.window().show_success("Supplier added successfully!")
            except Exception as e:
                self.window().show_error(f"Error: {e}")
            
    def order_supplies(self):
        """Place new order"""
        selected_sid = None
        row = self.table.currentRow()
        if row >= 0:
            selected_sid = int(self.table.item(row, 0).text())
            
        dialog = OrderSuppliesDialog(self, selected_sid)
        dialog.exec()
        
    def view_orders(self):
        """View history"""
        dialog = OrderHistoryDialog(self)
        dialog.exec()
            
    def edit_selected_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            self.window().show_warning("Please select a supplier to edit.")
            return
        sid = int(self.table.item(row, 0).text())
        sdata = self.supplier.get_supplier(sid)
        dialog = SupplierDialog(self, sdata)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.supplier.update_supplier(sid, **data)
                self.refresh_data()
                self.window().show_success("Supplier updated successfully!")
            except Exception as e:
                self.window().show_error(f"Error: {e}")
            
    def delete_selected_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            self.window().show_warning("Please select a supplier to delete.")
            return
        sid = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        if self.window().show_confirmation(f"Are you sure you want to delete supplier '{name}'?"):
            try:
                self.supplier.delete_supplier(sid)
                self.refresh_data()
                self.window().show_success("Supplier deleted.")
            except Exception as e:
                self.window().show_error(f"Error: {e}")
