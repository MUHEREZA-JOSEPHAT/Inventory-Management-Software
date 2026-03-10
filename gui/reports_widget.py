from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QDateEdit,
    QTabWidget, QComboBox
)
from PyQt6.QtCore import Qt, QDate
from models.product import Product
from models.inventory import Inventory
from models.sales import Sales

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.product = Product()
        self.inventory = Inventory()
        self.sales = Sales()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create header
        header = QHBoxLayout()
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_data)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.inventory_tab = QWidget()
        self.sales_tab = QWidget()
        self.low_stock_tab = QWidget()
        
        self.tabs.addTab(self.inventory_tab, "Inventory Status")
        self.tabs.addTab(self.sales_tab, "Sales Analysis")
        self.tabs.addTab(self.low_stock_tab, "Low Stock Alert")
        
        layout.addWidget(self.tabs)
        
        # Setup inventory tab
        self._setup_inventory_tab()
        
        # Setup sales tab
        self._setup_sales_tab()
        
        # Setup low stock tab
        self._setup_low_stock_tab()
    
    def _setup_inventory_tab(self):
        """Setup the inventory status tab"""
        layout = QVBoxLayout(self.inventory_tab)
        
        # Create table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Product", "Current Stock", "Reorder Point", "Status"
        ])
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.inventory_table)
        
        # Add summary
        self.inventory_summary = QLabel()
        self.inventory_summary.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.inventory_summary)
    
    def _setup_sales_tab(self):
        """Setup the sales analysis tab"""
        layout = QVBoxLayout(self.sales_tab)
        
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
        refresh_btn.clicked.connect(self._refresh_sales_data)
        date_layout.addWidget(refresh_btn)
        
        layout.addLayout(date_layout)
        
        # Add summary
        self.sales_summary = QLabel()
        self.sales_summary.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.sales_summary)
        
        # Create top products table
        layout.addWidget(QLabel("Top Selling Products"))
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Units Sold", "Total Revenue"
        ])
        
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.sales_table)
    
    def _setup_low_stock_tab(self):
        """Setup the low stock alert tab"""
        layout = QVBoxLayout(self.low_stock_tab)
        
        # Create table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            "ID", "Product", "Current Stock", "Reorder Point", "Status"
        ])
        
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.low_stock_table)
        
        # Add summary
        self.low_stock_summary = QLabel()
        self.low_stock_summary.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.low_stock_summary)
    
    def refresh_data(self):
        """Refresh all report data"""
        self._refresh_inventory_data()
        self._refresh_sales_data()
        self._refresh_low_stock_data()
    
    def _refresh_inventory_data(self):
        """Refresh inventory status data"""
        stock_levels = self.inventory.get_all_stock_levels()
        self.inventory_table.setRowCount(len(stock_levels))
        
        total_items = 0
        total_value = 0
        
        for row, level in enumerate(stock_levels):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(level[0])))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(level[1]))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(level[2])))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(level[3])))
            
            status_item = QTableWidgetItem(level[4])
            if level[4] == "Low Stock":
                status_item.setForeground(Qt.GlobalColor.red)
            self.inventory_table.setItem(row, 4, status_item)
            
            total_items += level[2]
        
        # Update summary
        self.inventory_summary.setText(
            f"Total Products: {len(stock_levels)} | "
            f"Total Items in Stock: {total_items}"
        )
    
    def _refresh_sales_data(self):
        """Refresh sales analysis data"""
        # Update summary
        summary = self.sales.get_sales_summary(
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd")
        )
        
        if summary and all(x is not None for x in summary):
            self.sales_summary.setText(
                f"Total Sales: {summary[0]} | "
                f"Total Units: {summary[1]} | "
                f"Total Revenue: ${summary[2]:,.2f} | "
                f"Average Sale: ${summary[3]:,.2f}"
            )
        else:
            self.sales_summary.setText(
                "No sales data available for the selected period"
            )
        
        # Update top products
        top_products = self.sales.get_top_selling_products(
            limit=10,
            start_date=self.start_date.date().toString("yyyy-MM-dd"),
            end_date=self.end_date.date().toString("yyyy-MM-dd")
        )
        
        self.sales_table.setRowCount(len(top_products))
        for row, product in enumerate(top_products):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.sales_table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.sales_table.setItem(row, 2, QTableWidgetItem(str(product[2])))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"${product[3]:,.2f}"))
    
    def _refresh_low_stock_data(self):
        """Refresh low stock alert data"""
        low_stock_products = self.product.get_low_stock_products()
        self.low_stock_table.setRowCount(len(low_stock_products))
        
        for row, product in enumerate(low_stock_products):
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(product[5])))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(product[4])))
            
            status_item = QTableWidgetItem("Low Stock")
            status_item.setForeground(Qt.GlobalColor.red)
            self.low_stock_table.setItem(row, 4, status_item)
        
        # Update summary
        self.low_stock_summary.setText(
            f"Low Stock Products: {len(low_stock_products)}"
        ) 