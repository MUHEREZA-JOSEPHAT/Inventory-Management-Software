import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QDateEdit,
    QTabWidget, QComboBox, QFrame, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, QDate
from models.product import Product
from models.inventory import Inventory
from models.sales import Sales

class TopProductsDialog(QDialog):
    def __init__(self, parent=None, top_products=None):
        super().__init__(parent)
        self.setWindowTitle("Top Selling Products")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Product", "Category", "Units Sold", "Total Revenue"])
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        if top_products:
            self.table.setRowCount(len(top_products))
            for row, product in enumerate(top_products):
                self.table.setItem(row, 0, QTableWidgetItem(product[1]))
                self.table.setItem(row, 1, QTableWidgetItem(product[4] if product[4] else "None"))
                self.table.setItem(row, 2, QTableWidgetItem(str(product[2])))
                self.table.setItem(row, 3, QTableWidgetItem(f"${product[3]:,.2f}"))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class KPICard(QFrame):
    def __init__(self, title, value, icon="", trend=None, color="#2575fc"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            KPICard {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e6ed;
            }}
            #card-title {{
                color: #7f8c8d;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            #card-value {{
                color: #2c3e50;
                font-size: 20px;
                font-weight: 800;
            }}
            #card-trend {{
                font-size: 10px;
                font-weight: 600;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("card-title")
        header.addWidget(title_label)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 20px; color: {color};")
        header.addStretch()
        header.addWidget(icon_label)
        layout.addLayout(header)
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("card-value")
        layout.addWidget(self.value_label)
        
        if trend is not None:
            self.trend_label = QLabel(trend)
            self.trend_label.setObjectName("card-trend")
            layout.addWidget(self.trend_label)

    def set_value(self, value, trend=None, trend_color="#2ecc71"):
        self.value_label.setText(value)
        if hasattr(self, 'trend_label') and trend:
            self.trend_label.setText(trend)
            self.trend_label.setStyleSheet(f"color: {trend_color};")

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.product = Product()
        self.inventory = Inventory()
        self.sales = Sales()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        self.setObjectName("reports-screen")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("5 ST★R Analytics")
        title.setStyleSheet("font-size: 28px; font-weight: 900; color: #1c2833;")
        
        refresh_btn = QPushButton(" 🔄 Refresh All")
        refresh_btn.setStyleSheet("background-color: #2575fc; color: white; padding: 10px 20px; font-weight: 700; border-radius: 8px;")
        refresh_btn.clicked.connect(self.refresh_data)
        
        self.top_products_btn = QPushButton(" 🏆 Top Selling Products")
        self.top_products_btn.setStyleSheet("background-color: #6a11cb; color: white; padding: 10px 20px; font-weight: 700; border-radius: 8px;")
        self.top_products_btn.clicked.connect(self._show_top_products)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.top_products_btn)
        header.addWidget(refresh_btn)
        layout.addLayout(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                padding: 12px 30px;
                background: transparent;
                color: #7f8c8d;
                font-weight: 600;
                border-bottom: 2px solid #e0e6ed;
            }
            QTabBar::tab:selected {
                color: #2575fc;
                border-bottom: 3px solid #2575fc;
                font-weight: 700;
            }
        """)
        
        self.inventory_tab = QWidget()
        self.sales_tab = QWidget()
        self.low_stock_tab = QWidget()
        
        self.tabs.addTab(self.inventory_tab, "Inventory Status")
        self.tabs.addTab(self.sales_tab, "Sales Analysis")
        self.tabs.addTab(self.low_stock_tab, "Low Stock Alert")
        
        layout.addWidget(self.tabs)
        
        self._setup_inventory_tab()
        self._setup_sales_tab()
        self._setup_low_stock_tab()
    
    def _setup_inventory_tab(self):
        layout = QVBoxLayout(self.inventory_tab)
        layout.setContentsMargins(0, 20, 0, 0)
        
        # Inventory Table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Product", "Category", "Current Stock", "Reorder Point", "Status"
        ])
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        for i in [2, 3, 4, 5]: header.setSectionResizeMode(i, header.ResizeMode.ResizeToContents)
        
        self.inventory_table.setColumnHidden(0, True)
        self.inventory_table.verticalHeader().setVisible(False)
        layout.addWidget(self.inventory_table)
        
        self.inventory_summary = QLabel()
        self.inventory_summary.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(self.inventory_summary)

    def _setup_sales_tab(self):
        main_layout = QVBoxLayout(self.sales_tab)
        main_layout.setContentsMargins(0, 20, 0, 0)
        main_layout.setSpacing(25)
        
        # Date Filter Row
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-30))
        self.end_date.setDate(today)
        
        filter_layout.addWidget(QLabel("Period:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.end_date)
        
        refresh_btn = QPushButton("Update View")
        refresh_btn.clicked.connect(self._refresh_sales_data)
        refresh_btn.setStyleSheet("background-color: #f8f9fa;")
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # KPI Row
        kpi_layout = QHBoxLayout()
        self.kpi_rev = KPICard("Total Revenue", "$0.00", "💰", "0% vs prev", color="#2ecc71")
        self.kpi_trans = KPICard("Transactions", "0", "🎟️", "0% vs prev", color="#3498db")
        self.kpi_units = KPICard("Units Sold", "0", "📦", "0% vs prev", color="#9b59b6")
        self.kpi_avg = KPICard("Avg Ticket", "$0.00", "📈", color="#f1c40f")
        
        kpi_layout.addWidget(self.kpi_rev)
        kpi_layout.addWidget(self.kpi_trans)
        kpi_layout.addWidget(self.kpi_units)
        kpi_layout.addWidget(self.kpi_avg)
        main_layout.addLayout(kpi_layout)
        
        # Grid for Comparative Table and Trend
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Comparison Table (Inspired by NetSuite)
        comp_container = QFrame()
        comp_container.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e0e6ed;")
        comp_layout = QVBoxLayout(comp_container)
        comp_layout.addWidget(QLabel("Key Performance Indicators (Monthly)"))
        
        self.comp_table = QTableWidget(3, 3)
        self.comp_table.setHorizontalHeaderLabels(["Indicator", "Current", "Previous"])
        self.comp_table.verticalHeader().setVisible(False)
        header = self.comp_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        self.comp_table.setItem(0, 0, QTableWidgetItem("Revenue"))
        self.comp_table.setItem(1, 0, QTableWidgetItem("Transactions"))
        self.comp_table.setItem(2, 0, QTableWidgetItem("Units Sold"))
        comp_layout.addWidget(self.comp_table)
        grid.addWidget(comp_container, 0, 0)
        
        # Daily Trend Chart
        trend_container = QFrame()
        trend_container.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e0e6ed;")
        trend_layout = QVBoxLayout(trend_container)
        trend_layout.addWidget(QLabel("Daily Sales Trend"))
        self.trend_plot = pg.PlotWidget()
        self.trend_plot.setBackground('w')
        trend_layout.addWidget(self.trend_plot)
        grid.addWidget(trend_container, 0, 1, 1, 2)
        grid.setColumnStretch(1, 2)
        grid.setRowStretch(0, 1) # Give all space to the first row (KPI + Chart)
        
        main_layout.addLayout(grid)

    def _show_top_products(self):
        """Show the top selling products in a dialog"""
        top_products = self.sales.get_top_selling_products(
            limit=50,
            start_date=self.start_date.date().toString("yyyy-MM-dd"),
            end_date=self.end_date.date().toString("yyyy-MM-dd")
        )
        dialog = TopProductsDialog(self, top_products)
        dialog.exec()

    def _setup_low_stock_tab(self):
        layout = QVBoxLayout(self.low_stock_tab)
        layout.setContentsMargins(0, 20, 0, 0)
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(6)
        self.low_stock_table.setHorizontalHeaderLabels([
            "ID", "Product", "Category", "Current Stock", "Reorder Point", "Status"
        ])
        
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        for i in [2, 3, 4, 5]: header.setSectionResizeMode(i, header.ResizeMode.ResizeToContents)
        
        self.low_stock_table.setColumnHidden(0, True)
        self.low_stock_table.verticalHeader().setVisible(False)
        layout.addWidget(self.low_stock_table)
        
        self.low_stock_summary = QLabel()
        self.low_stock_summary.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: 600; margin-top: 10px;")
        layout.addWidget(self.low_stock_summary)

    def refresh_data(self):
        self._refresh_inventory_data()
        self._refresh_sales_data()
        self._refresh_low_stock_data()

    def _refresh_inventory_data(self):
        stock_levels = self.inventory.get_all_stock_levels()
        self.inventory_table.setRowCount(len(stock_levels))
        total_items = 0
        for row, level in enumerate(stock_levels):
            # [0]ID, [1]Name, [2]Qty, [3]Reorder, [4]Status, [5]Unit, [6]Category
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(level[0])))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(level[1]))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(level[6] if level[6] else "None"))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(level[2])))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(str(level[3])))
            
            status_item = QTableWidgetItem(level[4])
            if level[4] == "Low Stock": status_item.setForeground(Qt.GlobalColor.red)
            self.inventory_table.setItem(row, 5, status_item)
            total_items += level[2]
            
        self.inventory_summary.setText(f"Total Products: {len(stock_levels)} | Total Items in Stock: {total_items}")

    def _refresh_sales_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        # Update KPI Cards
        summary = self.sales.get_sales_summary(start, end)
        if summary and all(x is not None for x in summary):
            self.kpi_trans.set_value(str(summary[0]))
            self.kpi_units.set_value(str(summary[1]))
            self.kpi_rev.set_value(f"${summary[2]:,.2f}")
            self.kpi_avg.set_value(f"${summary[3]:,.2f}")
            
        # Update Monthly Comparison
        comp = self.sales.get_sales_summary_comparison()
        curr, prev = comp['current'], comp['previous']
        
        for i, (v_curr, v_prev) in enumerate([
            (curr['revenue'], prev['revenue']),
            (curr['transactions'], prev['transactions']),
            (curr['units'], prev['units'])
        ]):
            curr_str = f"${v_curr:,.2f}" if i == 0 else str(v_curr)
            prev_str = f"${v_prev:,.2f}" if i == 0 else str(v_prev)
            self.comp_table.setItem(i, 1, QTableWidgetItem(curr_str))
            self.comp_table.setItem(i, 2, QTableWidgetItem(prev_str))
            
            # Calculate trends for KPI cards
            if i == 0: # Revenue trend
                pct = ((v_curr - v_prev) / v_prev * 100) if v_prev > 0 else 0
                color = "#2ecc71" if pct >= 0 else "#e74c3c"
                self.kpi_rev.set_value(f"${v_curr:,.2f}", f"{pct:+.1f}% vs last month", trend_color=color)

        # Update Trend Chart
        trend_data = self.sales.get_daily_sales_trend(start, end)
        self.trend_plot.clear()
        if trend_data:
            revenues = [d[1] for d in trend_data]
            x = np.arange(len(revenues))
            line = self.trend_plot.plot(x, revenues, pen=pg.mkPen('#2575fc', width=3), symbol='o', symbolSize=8)
            # Add labels if possible, but for now just the line
            self.trend_plot.setLabel('left', 'Revenue', units='$')
            self.trend_plot.showGrid(x=True, y=True, alpha=0.3)

    def _refresh_low_stock_data(self):
        low_stock_products = self.product.get_low_stock_products()
        self.low_stock_table.setRowCount(len(low_stock_products))
        for row, product in enumerate(low_stock_products):
            # [0]ID, [1]Name, [2]Qty, [3]Price, [4]Reorder, [5]Unit, [6]CreatedAt, [7]Category
            # Wait, Product.get_low_stock_products order check...
            # From models/product.py: SELECT product_id, name, quantity... [7] is category_name
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(str(product[0])))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(product[1]))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(product[7] if product[7] else "None"))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(product[2])))
            self.low_stock_table.setItem(row, 4, QTableWidgetItem(str(product[4])))
            item = QTableWidgetItem("Low Stock")
            item.setForeground(Qt.GlobalColor.red)
            self.low_stock_table.setItem(row, 5, item)
            
        self.low_stock_summary.setText(f"Low Stock Products: {len(low_stock_products)}")