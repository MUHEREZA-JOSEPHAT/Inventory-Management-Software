from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QLabel, QDateEdit, QComboBox,
    QAbstractSpinBox, QCompleter, QHeaderView, QFrame,
    QSplitter, QAbstractItemView, QLineEdit
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont, QIcon
from models.sales import Sales
from models.product import Product
from models.category import Category

class AddToCartDialog(QDialog):
    """Small popup to specify quantity for a selected product"""
    def __init__(self, parent=None, product_name="", price=0.0, stock=0, unit="piece"):
        super().__init__(parent)
        self.setWindowTitle("Add to Cart")
        self.setMinimumWidth(350)
        self.price = price
        self.stock = stock
        self.unit = unit
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        title = QLabel(f"Adding: {product_name}")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addRow(title)
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, stock if stock > 0 else 1)
        self.qty_spin.setValue(1)
        self.qty_spin.setStyleSheet("padding: 5px; font-size: 14px;")
        
        price_label = QLabel(f"Unit Price: ${price:,.2f}")
        layout.addRow("Quantity:", self.qty_spin)
        layout.addRow(price_label)
        
        self.total_label = QLabel(f"Total: ${price:,.2f}")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71;")
        layout.addRow(self.total_label)
        
        self.qty_spin.valueChanged.connect(self._update_total)
        
        btns = QHBoxLayout()
        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        add_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(add_btn)
        btns.addWidget(cancel_btn)
        layout.addRow("", btns)

    def _update_total(self):
        total = self.qty_spin.value() * self.price
        self.total_label.setText(f"Total: ${total:,.2f}")
        
    def get_quantity(self):
        return self.qty_spin.value()

class NewSaleWindow(QDialog):
    """Advanced POS Window with product search and shopping cart"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("5 ST★R Point of Sale")
        self.setMinimumSize(1000, 600)
        self.product_model = Product()
        self.category_model = Category()
        self.cart_items = [] # List of dicts: {id, name, qty, price, total}
        self.setup_ui()
        self._load_products()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10) # Reduced top margin
        main_layout.setSpacing(10) # Reduced spacing
        
        # Top Header Area
        header = QHBoxLayout()
        title = QLabel("🛒 POS Checkout")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1c2833; margin-top: 0px;")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Splitter for Products (Left) and Cart (Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT SIDE: PRODUCT DISCOVERY ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Search Filters
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by product name...")
        self.search_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #dcdde1;")
        self.search_input.textChanged.connect(self._filter_products)
        
        self.cat_filter = QComboBox()
        self.cat_filter.addItem("All Categories", None)
        cats = self.category_model.get_all_categories()
        for cat in cats:
            self.cat_filter.addItem(cat[1], cat[0])
        self.cat_filter.setStyleSheet("padding: 8px; min-width: 150px;")
        self.cat_filter.currentIndexChanged.connect(self._filter_products)
        
        filters.addWidget(self.search_input, 3)
        filters.addWidget(self.cat_filter, 1)
        left_layout.addLayout(filters)
        
        # Products Table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5) # ID, Name, Category, Price, Stock
        self.product_table.setHorizontalHeaderLabels(["ID", "Product Name", "Category", "Price", "Stock"])
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setColumnHidden(0, True)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.doubleClicked.connect(self._on_product_double_clicked)
        
        h = self.product_table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in [2, 3, 4]: h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        left_layout.addWidget(self.product_table)
        splitter.addWidget(left_widget)
        
        # --- RIGHT SIDE: SHOPPING CART ---
        right_widget = QFrame()
        right_widget.setObjectName("cart-frame")
        right_widget.setStyleSheet("QFrame#cart-frame { background: white; border-radius: 10px; border: 1px solid #e0e6ed; }")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 5, 15, 10) # Reduced top margin
        
        cart_title = QLabel("🛍️ Shopping Cart")
        cart_title.setStyleSheet("font-weight: bold; font-size: 16px; margin: 0px;")
        right_layout.addWidget(cart_title)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5) # ID, Product, Qty, Total, Action
        self.cart_table.setHorizontalHeaderLabels(["ID", "Product", "Qty", "Total", "Action"])
        self.cart_table.setColumnHidden(0, True)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setStyleSheet("border: none;")
        
        ch = self.cart_table.horizontalHeader()
        ch.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in [2, 3, 4]: ch.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        right_layout.addWidget(self.cart_table)
        
        # Totals and Checkout
        self.grand_total_label = QLabel("Grand Total: $0.00")
        self.grand_total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2ecc71; margin-top: 10px;")
        right_layout.addWidget(self.grand_total_label, 0, Qt.AlignmentFlag.AlignRight)
        
        self.checkout_btn = QPushButton("Complete Sale")
        self.checkout_btn.setStyleSheet("background-color: #2575fc; color: white; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px;")
        self.checkout_btn.clicked.connect(self.accept)
        right_layout.addWidget(self.checkout_btn)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([650, 450])
        main_layout.addWidget(splitter)
        
        # Pull everything up
        main_layout.addStretch(1)

    def _load_products(self):
        products = self.product_model.get_all_products()
        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            # p: [0]ID, [1]Name, [2]Qty, [3]Price, [4]Reorder, [5]Unit, [6]CreatedAt, [7]Category
            self.product_table.setItem(row, 0, QTableWidgetItem(str(p[0])))
            self.product_table.setItem(row, 1, QTableWidgetItem(p[1]))
            self.product_table.setItem(row, 2, QTableWidgetItem(p[7] if p[7] else "None"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"${p[3]:,.2f}"))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(p[2])))
            
    def _filter_products(self):
        search = self.search_input.text().lower()
        cat_id = self.cat_filter.currentData()
        cat_name = self.cat_filter.currentText().lower()
        
        for row in range(self.product_table.rowCount()):
            name = self.product_table.item(row, 1).text().lower()
            cat = self.product_table.item(row, 2).text().lower()
            
            match_search = search in name or search in cat
            match_cat = (cat_id is None) or (cat_name == cat)
            
            self.product_table.setRowHidden(row, not (match_search and match_cat))

    def _on_product_double_clicked(self, index):
        row = index.row()
        pid = int(self.product_table.item(row, 0).text())
        name = self.product_table.item(row, 1).text()
        price_str = self.product_table.item(row, 3).text().replace("$", "").replace(",", "")
        price = float(price_str)
        stock = int(self.product_table.item(row, 4).text())
        
        dialog = AddToCartDialog(self, name, price, stock)
        if dialog.exec():
            qty = dialog.get_quantity()
            self._add_to_cart(pid, name, qty, price)

    def _add_to_cart(self, pid, name, qty, price):
        # Check if already in cart
        for item in self.cart_items:
            if item['id'] == pid:
                item['qty'] += qty
                item['total'] = item['qty'] * item['price']
                self._refresh_cart_table()
                return
        
        # New item
        self.cart_items.append({
            'id': pid,
            'name': name,
            'qty': qty,
            'price': price,
            'total': qty * price
        })
        self._refresh_cart_table()

    def _refresh_cart_table(self):
        self.cart_table.setRowCount(len(self.cart_items))
        total_revenue = 0
        for row, item in enumerate(self.cart_items):
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['qty'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"${item['total']:,.2f}"))
            
            # Action buttons
            actions = QHBoxLayout()
            actions.setContentsMargins(0, 0, 0, 0)
            actions.setSpacing(5)
            
            edit_btn = QPushButton("✎")
            edit_btn.setToolTip("Edit quantity")
            edit_btn.setStyleSheet("color: #2575fc; font-weight: bold; border: none; background: transparent;")
            edit_btn.clicked.connect(lambda _, r=row: self._edit_cart_item(r))
            
            remove_btn = QPushButton("✖")
            remove_btn.setToolTip("Remove from cart")
            remove_btn.setStyleSheet("color: red; font-weight: bold; border: none; background: transparent;")
            remove_btn.clicked.connect(lambda _, r=row: self._remove_from_cart(r))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(remove_btn)
            
            self.cart_table.setCellWidget(row, 4, action_widget)
            
            total_revenue += item['total']
            
        self.grand_total_label.setText(f"Grand Total: ${total_revenue:,.2f}")

    def _edit_cart_item(self, row):
        if 0 <= row < len(self.cart_items):
            item = self.cart_items[row]
            # Get current stock for this product
            product = self.product_model.get_product(item['id'])
            stock = product[2] if product else item['qty']
            
            dialog = AddToCartDialog(self, item['name'], item['price'], stock)
            dialog.qty_spin.setValue(item['qty'])
            dialog.setWindowTitle("Edit Cart Item")
            
            if dialog.exec():
                item['qty'] = dialog.get_quantity()
                item['total'] = item['qty'] * item['price']
                self._refresh_cart_table()

    def _remove_from_cart(self, row):
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self._refresh_cart_table()

    def get_cart_data(self):
        return self.cart_items

class SalesHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales History")
        self.setMinimumSize(900, 600)
        self.sales = Sales()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
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
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # ID, Product, Category, Qty, Price, Total, Date
        self.table.setHorizontalHeaderLabels([
            "Sale ID", "Product", "Category", "Quantity", "Price", "Total", "Date"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px;")
        summary_layout.addWidget(self.summary_label)
        layout.addLayout(summary_layout)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.refresh_data()
    
    def refresh_data(self):
        sales = self.sales.get_sales_by_date_range(
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        )
        
        self.table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(sale[0])))
            self.table.setItem(row, 1, QTableWidgetItem(sale[1]))
            self.table.setItem(row, 2, QTableWidgetItem(sale[6] if sale[6] else "None"))
            self.table.setItem(row, 3, QTableWidgetItem(str(sale[2])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${sale[3]:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${sale[4]:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(str(sale[5])))
        
        summary = self.sales.get_sales_summary(
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        )
        
        if summary and all(x is not None for x in summary):
            self.summary_label.setText(
                f"Total Sales: {summary[0]} | "
                f"Total Units: {summary[1]} | "
                f"Total Revenue: ${summary[2]:,.2f} | "
                f"Average Sale: ${summary[3]:,.2f}"
            )
        else:
            self.summary_label.setText("No sales data available")

class SalesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.sales = Sales()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        title = QLabel("5 ST★R Sales")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #1c2833;")
        
        new_sale_btn = QPushButton(" 🛒 New Sale")
        new_sale_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px 20px; font-weight: 700; border-radius: 8px;")
        history_btn = QPushButton(" 🕒 Sales History")
        history_btn.setStyleSheet("background-color: #2575fc; color: white; padding: 10px 20px; font-weight: 700; border-radius: 8px;")
        refresh_btn = QPushButton(" 🔄 Refresh")
        
        new_sale_btn.clicked.connect(self.new_sale)
        history_btn.clicked.connect(self.view_history)
        refresh_btn.clicked.connect(self.refresh_data)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(new_sale_btn)
        header.addWidget(history_btn)
        header.addWidget(refresh_btn)
        layout.addLayout(header)
        
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(self.summary_label)
        
        layout.addWidget(QLabel("Top Selling Products"))
        self.table = QTableWidget()
        self.table.setColumnCount(5) # ID, Name, Category, Units, Rev
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Category", "Units Sold", "Total Revenue"
        ])
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in [2, 3, 4]: h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
    
    def refresh_data(self):
        summary = self.sales.get_sales_summary()
        if summary and all(x is not None for x in summary):
            self.summary_label.setText(
                f"Total Sales: {summary[0]} | "
                f"Total Units: {summary[1]} | "
                f"Total Revenue: ${summary[2]:,.2f} | "
                f"Average Sale: ${summary[3]:,.2f}"
            )
        else:
            self.summary_label.setText("No sales data available")
        
        top_products = self.sales.get_top_selling_products(limit=10)
        self.table.setRowCount(len(top_products))
        
        for row, product in enumerate(top_products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QTableWidgetItem(product[4] if product[4] else "None"))
            self.table.setItem(row, 3, QTableWidgetItem(str(product[2])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${product[3]:,.2f}"))

    def filter_data(self, search_term):
        """Filter the top selling products table"""
        search_term = search_term.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            cat_item = self.table.item(row, 2)
            match = not search_term
            if not match:
                if name_item and search_term in name_item.text().lower(): match = True
                elif cat_item and search_term in cat_item.text().lower(): match = True
            self.table.setRowHidden(row, not match)
    
    def new_sale(self):
        """Launch the Advanced POS Window"""
        window = NewSaleWindow(self)
        if window.exec():
            cart_data = window.get_cart_data()
            if not cart_data:
                return
                
            success_count = 0
            for item in cart_data:
                try:
                    if self.sales.record_sale(item['id'], item['qty'], item['price']):
                        success_count += 1
                except Exception as e:
                    print(f"Error recording item {item['name']}: {e}")
            
            if success_count == len(cart_data):
                self.window().show_success(f"Sale completed successfully! {success_count} items processed.")
            else:
                self.window().show_warning(f"Sale partial success: {success_count}/{len(cart_data)} items processed.")
            
            self.refresh_data()
    
    def view_history(self):
        dialog = SalesHistoryDialog(self)
        dialog.exec()