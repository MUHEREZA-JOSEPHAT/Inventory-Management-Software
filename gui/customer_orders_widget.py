from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QScrollArea, QSplitter, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from models.customer_order import CustomerOrder

class ChatBalloon(QFrame):
    """A graphical chat balloon for order messages"""
    def __init__(self, sender, message, timestamp, is_self=False):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(2)
        
        bg_color = "#e3f2fd" if not is_self else "#2575fc"
        text_color = "#1c2833" if not is_self else "white"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                border: none;
                margin: 5px;
            }}
            QLabel {{
                background: transparent;
                color: {text_color};
                border: none;
            }}
        """)
        
        sender_lbl = QLabel(sender)
        sender_lbl.setStyleSheet(f"font-weight: bold; font-size: 10px; color: {text_color};")
        
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"font-size: 13px; color: {text_color};")
        
        time_text = timestamp.split()[1] if ' ' in timestamp else timestamp
        time_lbl = QLabel(time_text)
        time_lbl.setStyleSheet(f"font-size: 9px; color: {text_color}; opacity: 0.7;")
        
        self.layout.addWidget(sender_lbl)
        self.layout.addWidget(msg_lbl)
        self.layout.addWidget(time_lbl, 0, Qt.AlignmentFlag.AlignRight)
        
        self.setMaximumWidth(250)

class CustomerOrdersWidget(QWidget):
    def __init__(self, current_user="Admin"):
        super().__init__()
        self.model = CustomerOrder()
        self.current_user = current_user
        self.selected_order_id = None
        self.last_message_count = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_chat)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout for the entire widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Centering container
        center_wrapper = QWidget()
        center_wrapper_layout = QHBoxLayout(center_wrapper)
        center_wrapper_layout.setContentsMargins(30, 30, 30, 30)
        center_wrapper_layout.addStretch(1) # Left Stretch
        
        # Content box
        content_box = QWidget()
        content_box.setMinimumWidth(800)
        content_box.setMaximumWidth(1000)
        content_layout = QVBoxLayout(content_box)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(25)
        
        # Title and Header Area
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        title = QLabel("Online Customer Chat")
        title.setStyleSheet("font-size: 28px; font-weight: 900; color: #1c2833;")
        header_layout.addWidget(title)
        
        # Order Dropdown Selection
        selection_label = QLabel("Select a customer order to start chatting:")
        selection_label.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: 600;")
        header_layout.addWidget(selection_label)
        
        self.order_dropdown = QComboBox()
        self.order_dropdown.setPlaceholderText("Select an active order...")
        self.order_dropdown.setStyleSheet("""
            QComboBox {
                padding: 12px 20px;
                border-radius: 12px;
                border: 2px solid #e0e6ed;
                background-color: white;
                font-size: 15px;
                color: #2c3e50;
                min-width: 400px;
            }
            QComboBox:hover {
                border-color: #2575fc;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2575fc;
                margin-right: 15px;
            }
        """)
        self.order_dropdown.currentIndexChanged.connect(self.on_dropdown_changed)
        header_layout.addWidget(self.order_dropdown)
        
        content_layout.addWidget(header_container)
        
        # Main Chat Area
        self.right_container = QFrame()
        self.right_container.setObjectName("chat-panel")
        self.right_container.setStyleSheet("""
            #chat-panel {
                background: white; 
                border-radius: 15px; 
                border: 1px solid #e0e6ed;
                min-height: 500px;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder view when no order selected
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder_icon = QLabel("💬")
        placeholder_icon.setStyleSheet("font-size: 64px; margin-bottom: 10px;")
        placeholder_layout.addWidget(placeholder_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        placeholder_text = QLabel("Choose a customer from the dropdown above\nto view order details and history.")
        placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_text.setStyleSheet("color: #95a5a6; font-size: 16px; font-weight: 500;")
        placeholder_layout.addWidget(placeholder_text)
        
        self.right_layout.addWidget(self.placeholder_widget)
        
        # Actual Chat View container (Hidden initially)
        self.chat_view_container = QWidget()
        self.chat_view_layout = QVBoxLayout(self.chat_view_container)
        self.chat_view_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_view_layout.setSpacing(15)
        
        # Order info banner
        self.info_banner = QFrame()
        self.info_banner.setStyleSheet("background-color: #f1f8ff; border-radius: 10px; border: 1px solid #c8e1ff;")
        banner_layout = QHBoxLayout(self.info_banner)
        
        self.order_details_lbl = QLabel("")
        self.order_details_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #0366d6;")
        
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["New", "In Progress", "Completed", "Cancelled"])
        self.status_dropdown.setFixedWidth(150)
        self.status_dropdown.currentTextChanged.connect(self.change_order_status)
        self.status_dropdown.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border-radius: 5px;
                border: 1px solid #c8e1ff;
                background: white;
                font-weight: 600;
            }
        """)
        
        banner_layout.addWidget(self.order_details_lbl)
        banner_layout.addStretch()
        banner_layout.addWidget(QLabel("Status:"))
        banner_layout.addWidget(self.status_dropdown)
        self.chat_view_layout.addWidget(self.info_banner)
        
        # Scrollable messages area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: #f8f9fa; border-radius: 10px; border: none;")
        self.message_container = QWidget()
        self.message_container.setStyleSheet("background: transparent;")
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.addStretch()
        self.scroll.setWidget(self.message_container)
        self.chat_view_layout.addWidget(self.scroll)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Write a message to the customer...")
        self.msg_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px; 
                border-radius: 25px; 
                border: 1px solid #e0e6ed;
                background-color: white;
                font-size: 14px;
            }
        """)
        self.msg_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send Message")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2575fc; 
                color: white; 
                border-radius: 25px; 
                padding: 10px 25px; 
                font-weight: 800;
                text-transform: uppercase;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1a5fdb;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.msg_input)
        input_layout.addWidget(self.send_btn)
        self.chat_view_layout.addLayout(input_layout)
        
        self.right_layout.addWidget(self.chat_view_container)
        self.chat_view_container.hide()
        
        content_layout.addWidget(self.right_container)
        
        center_wrapper_layout.addWidget(content_box)
        center_wrapper_layout.addStretch(1) # Right Stretch
        
        main_layout.addStretch(1)
        main_layout.addWidget(center_wrapper)
        main_layout.addStretch(1)
        
        # For compatibility if any other code still expects self.table
        self.table = QTableWidget() 
        
        self.refresh_data()


        
    def refresh_data(self):
        """Reload the orders list into the dropdown"""
        self.orders_list = self.model.get_all_orders()
        self.order_dropdown.blockSignals(True)
        self.order_dropdown.clear()
        self.order_dropdown.addItem("Select an active order...", None)
        
        for order in self.orders_list:
            # order[0] is order_id, order[1] is customer_name
            display_text = f"📦 Order #{order[0]} - {order[1]}"
            self.order_dropdown.addItem(display_text, order[0])
            
        self.order_dropdown.blockSignals(False)

    def on_dropdown_changed(self, index):
        order_id = self.order_dropdown.currentData()
        
        if not order_id:
            self.chat_view_container.hide()
            self.placeholder_widget.show()
            self.selected_order_id = None
            self.timer.stop()
            return
            
        # Find order details in the cached list
        order = next((o for o in self.orders_list if o[0] == order_id), None)
        if not order: return
        
        self.selected_order_id = order_id
        cust_name = order[1]
        product_details = f"{order[2]} (x{order[3]})"
        status = order[5]
        
        self.order_details_lbl.setText(f"Chatting with {cust_name} | Product: {product_details}")
        
        # [NEW] Mark as read when selected
        self.model.mark_as_read(order_id)
        
        # Set dropdown box to current status without triggering signal
        self.status_dropdown.blockSignals(True)
        self.status_dropdown.setCurrentText(status)
        self.status_dropdown.blockSignals(False)
        
        self.placeholder_widget.hide()
        self.chat_view_container.show()
        
        self.last_message_count = -1 # force refresh
        self.refresh_chat()
        self.timer.start(2000) # start polling chat

    def change_order_status(self, new_status):
        """Update the status in the database and refresh"""
        if self.selected_order_id:
            self.model.update_order_status(self.selected_order_id, new_status)
            self.refresh_data()
            # We don't want to clear the chat, so we just update the banner if needed
            self.order_details_lbl.setText(f"Status updated to: {new_status}")

    def on_order_selected(self):
        # Deprecated by dropdown, but kept for safety if called elsewhere
        pass


    def send_message(self):
        if not self.selected_order_id: return
        text = self.msg_input.text().strip()
        if not text: return
        
        self.model.send_order_message(self.selected_order_id, self.current_user, text)
        self.msg_input.clear()
        self.refresh_chat()
        
        # Auto scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))
        
        # Simulate Customer Reply for demo purposes if it's a specific message
        if "hello" in text.lower() or "hi" in text.lower():
            QTimer.singleShot(1500, lambda: self._simulate_customer("Hello! Has my order shipped yet?"))
        elif "yes" in text.lower() or "shipped" in text.lower() or "prepared" in text.lower():
            QTimer.singleShot(1500, lambda: self._simulate_customer("Awesome, thank you!"))

    def _simulate_customer(self, message):
        if self.selected_order_id:
            self.model.add_simulated_customer_message(self.selected_order_id, message)
            self.refresh_chat()

    def refresh_chat(self):
        if not self.selected_order_id: return
        
        messages = self.model.get_order_messages(self.selected_order_id)
        if len(messages) == self.last_message_count:
            return
            
        # Clear layout properly
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Cleanup any layout items from old version just in case
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
        self.last_message_count = len(messages)
        for sender, message, timestamp in messages:
            is_self = (sender == self.current_user)
            balloon = ChatBalloon(sender, message, timestamp, is_self)
            
            # Use Alignment flag directly instead of sub-layout
            align = Qt.AlignmentFlag.AlignRight if is_self else Qt.AlignmentFlag.AlignLeft
            self.message_layout.insertWidget(self.message_layout.count() - 1, balloon, 0, align)
            
        # Ensure scroll is down initially if messages loaded
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))
