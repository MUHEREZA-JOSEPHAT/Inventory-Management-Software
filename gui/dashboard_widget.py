import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.product import Product
from models.sales import Sales
from models.inventory import Inventory

class CompactStatCard(QFrame):
    def __init__(self, title, value, icon_char, color="#2575fc"):
        super().__init__()
        self.setObjectName("stat-card")
        self.setStyleSheet(f"""
            #stat-card {{
                background-color: white;
                border-radius: 12px;
                border-bottom: 2px solid {color};
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon/Symbol
        icon_label = QLabel(icon_char)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: bold; text-transform: uppercase;")
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: #2c3e50; font-size: 22px; font-weight: 800;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        layout.addLayout(text_layout)
        layout.addStretch()

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.product_model = Product()
        self.sales_model = Sales()
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25)
        
        # Header with branding context
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard Overview")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)
        
        # Stats Cards Grid
        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)
        
        self.card_products = CompactStatCard("Total Products", "0", "📦", "#3498db")
        self.card_low_stock = CompactStatCard("Low Stock Items", "0", "⚠️", "#e74c3c")
        self.card_sales = CompactStatCard("Total Orders", "0", "🛍️", "#2ecc71")
        self.card_revenue = CompactStatCard("Gross Revenue", "$0.00", "💰", "#f1c40f")
        
        stats_container.addWidget(self.card_products)
        stats_container.addWidget(self.card_low_stock)
        stats_container.addWidget(self.card_sales)
        stats_container.addWidget(self.card_revenue)
        
        self.layout.addLayout(stats_container)
        
        # Middle Section: Tables and Charts (borrowed from Image 1 & 3)
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(30)
        
        # Sales Bar Chart
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        chart_layout.addWidget(QLabel("Sales Performance (Recent Products)"))
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        chart_layout.addWidget(self.plot_widget)
        mid_layout.addWidget(chart_frame, 2)
        
        # Quick Alerts/Summary (Image 1 style)
        self.alert_frame = QFrame()
        self.alert_frame.setStyleSheet("background-color: white; border-radius: 12px;")
        alert_layout = QVBoxLayout(self.alert_frame)
        alert_layout.setContentsMargins(20, 20, 20, 20)
        alert_layout.addWidget(QLabel("Recent Alerts"))
        self.alert_list = QLabel("All products are well stocked!")
        self.alert_list.setStyleSheet("color: #95a5a6; font-size: 14px;")
        self.alert_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alert_layout.addWidget(self.alert_list)
        alert_layout.addStretch()
        mid_layout.addWidget(self.alert_frame, 1)
        
        self.layout.addLayout(mid_layout, 1)

    def refresh_data(self):
        products = self.product_model.get_all_products()
        sales_summary = self.sales_model.get_sales_summary()
        low_stock = self.product_model.get_low_stock_products()
        
        self.card_products.value_label.setText(str(len(products)))
        self.card_low_stock.value_label.setText(str(len(low_stock)))
        
        rev = sales_summary[2] if sales_summary and sales_summary[2] else 0.0
        orders = sales_summary[0] if sales_summary and sales_summary[0] else 0
        
        self.card_sales.value_label.setText(str(orders))
        self.card_revenue.value_label.setText(f"${rev:,.2f}")
        
        # Update Chart
        self.plot_widget.clear()
        top_selling = self.sales_model.get_top_selling_products(limit=6)
        if top_selling:
            import pyqtgraph as pg
            import numpy as np
            
            names = [p[1][:10] + ".." if len(p[1]) > 10 else p[1] for p in top_selling]
            values = [p[3] for p in top_selling]
            x = np.arange(len(values))
            
            # Set labels on X axis
            xax = self.plot_widget.getAxis('bottom')
            ticks = [list(zip(x, names))]
            xax.setTicks(ticks)
            
            bargraph = pg.BarGraphItem(x=x, height=values, width=0.5, brush='#2575fc')
            self.plot_widget.addItem(bargraph)
        
        # Update Alerts with "Notification Card" style
        # Clear existing alerts
        for i in reversed(range(self.alert_frame.layout().count())):
            item = self.alert_frame.layout().itemAt(i)
            if item.widget() and item.widget().objectName() == "alert-item":
                item.widget().setParent(None)

        if low_stock:
            self.alert_list.hide()
            for p in low_stock[:4]:
                item = QFrame()
                item.setObjectName("alert-item")
                item.setStyleSheet("""
                    #alert-item {
                        background-color: #fff5f5;
                        border-left: 4px solid #e74c3c;
                        border-radius: 4px;
                        margin-bottom: 5px;
                    }
                """)
                l = QHBoxLayout(item)
                txt = QLabel(f"<b>{p[1]}</b> is low on stock! ({p[2]} left)")
                txt.setStyleSheet("color: #c0392b; font-size: 13px;")
                l.addWidget(txt)
                self.alert_frame.layout().insertWidget(1, item)
        else:
            self.alert_list.show()
            self.alert_list.setText("All products are well stocked!")
