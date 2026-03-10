from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QLabel, QDateEdit, QComboBox,
    QAbstractSpinBox, QCompleter
)
from PyQt6.QtCore import Qt, QDate
from models.sales import Sales
from models.product import Product

class NewSaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Sale")
        self.setMinimumWidth(400)
        self.product = Product()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Create form fields
        self.product_combo = QComboBox()
        self._populate_products()
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(1)
        
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$")
        # Unit price is determined by selected product and is read-only
        self.price_spin.setReadOnly(True)
        self.price_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        # Connect product selection to price update
        self.product_combo.currentIndexChanged.connect(self._update_price)
        
        # Add fields to form
        layout.addRow("Product:", self.product_combo)
        layout.addRow("Quantity:", self.quantity_spin)
        layout.addRow("Price:", self.price_spin)
        
        # Add total label
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addRow("Total:", self.total_label)
        
        # Connect quantity and price changes to total update
        self.quantity_spin.valueChanged.connect(self._update_total)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def _populate_products(self):
        """Populate the product combo box"""
        products = self.product.get_all_products()
        display_texts = []
        for product in products:
            text = f"{product[1]} (Stock: {product[2]} {product[5]})"
            display_texts.append(text)
            self.product_combo.addItem(
                text,
                product[0]  # Store product ID as user data
            )

        # Make the combo box searchable
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = QCompleter(display_texts, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # Allow matching text contained anywhere in the product string
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_combo.setCompleter(completer)
    
    def _update_price(self):
        """Update price when product is selected"""
        product_id = self.product_combo.currentData()
        if product_id:
            product = self.product.get_product(product_id)
            if product:
                self.price_spin.setValue(product[3])
                # Whenever unit price changes, refresh total
                self._update_total()
    
    def _update_total(self):
        """Update total when quantity or price changes"""
        total = self.quantity_spin.value() * self.price_spin.value()
        self.total_label.setText(f"${total:.2f}")
    
    def get_data(self):
        return {
            'product_id': self.product_combo.currentData(),
            'quantity': self.quantity_spin.value(),
            'price': self.price_spin.value()
        }

class SalesHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales History")
        self.setMinimumSize(800, 600)
        self.sales = Sales()
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Sale ID", "Product", "Quantity", "Price", "Total", "Date"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Add summary section
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px;")
        summary_layout.addWidget(self.summary_label)
        layout.addLayout(summary_layout)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the sales history data"""
        sales = self.sales.get_sales_by_date_range(
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        )
        
        self.table.setRowCount(len(sales))
        total_revenue = 0
        total_units = 0
        
        for row, sale in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(sale[0])))
            self.table.setItem(row, 1, QTableWidgetItem(sale[1]))
            self.table.setItem(row, 2, QTableWidgetItem(str(sale[2])))
            self.table.setItem(row, 3, QTableWidgetItem(f"${sale[3]:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${sale[4]:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(sale[5])))
            
            total_revenue += sale[4]
            total_units += sale[2]
        
        # Update summary
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
            self.summary_label.setText(
                "No sales data available for the selected period"
            )

class SalesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.sales = Sales()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create header with title and buttons
        header = QHBoxLayout()
        title = QLabel("Sales Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        new_sale_btn = QPushButton("New Sale")
        history_btn = QPushButton("Sales History")
        refresh_btn = QPushButton("Refresh")
        
        new_sale_btn.clicked.connect(self.new_sale)
        history_btn.clicked.connect(self.view_history)
        refresh_btn.clicked.connect(self.refresh_data)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(new_sale_btn)
        header.addWidget(history_btn)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Create summary section
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(self.summary_label)
        
        # Create top products table
        layout.addWidget(QLabel("Top Selling Products"))
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Units Sold", "Total Revenue"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
    
    def refresh_data(self):
        """Refresh the sales data"""
        # Update summary
        summary = self.sales.get_sales_summary()
        if summary and all(x is not None for x in summary):
            self.summary_label.setText(
                f"Total Sales: {summary[0]} | "
                f"Total Units: {summary[1]} | "
                f"Total Revenue: ${summary[2]:,.2f} | "
                f"Average Sale: ${summary[3]:,.2f}"
            )
        else:
            self.summary_label.setText(
                "No sales data available"
            )
        
        # Update top products
        top_products = self.sales.get_top_selling_products(limit=10)
        self.table.setRowCount(len(top_products))
        
        for row, product in enumerate(top_products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QTableWidgetItem(str(product[2])))
            self.table.setItem(row, 3, QTableWidgetItem(f"${product[3]:,.2f}"))
    
    def new_sale(self):
        """Show dialog to record a new sale"""
        dialog = NewSaleDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if self.sales.record_sale(
                    data['product_id'],
                    data['quantity'],
                    data['price']
                ):
                    self.refresh_data()
                    self.window().show_success("Sale recorded successfully!")
                else:
                    self.window().show_error("Failed to record sale")
            except Exception as e:
                self.window().show_error(f"Error recording sale: {str(e)}")
    
    def view_history(self):
        """Show sales history dialog"""
        dialog = SalesHistoryDialog(self)
        dialog.exec() 