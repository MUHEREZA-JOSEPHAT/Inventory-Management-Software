from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTextEdit, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from models.chat import Chat

class ChatBalloon(QFrame):
    """A graphical chat balloon for messages"""
    def __init__(self, sender, message, timestamp, is_self=False):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(2)
        
        bg_color = "#e3f2fd" if not is_self else "#2575fc"
        text_color = "#1c2833" if not is_self else "white"
        align = Qt.AlignmentFlag.AlignLeft if not is_self else Qt.AlignmentFlag.AlignRight
        
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
        
        time_lbl = QLabel(timestamp.split()[1] if ' ' in timestamp else timestamp)
        time_lbl.setStyleSheet(f"font-size: 9px; color: {text_color}; opacity: 0.7;")
        
        self.layout.addWidget(sender_lbl)
        self.layout.addWidget(msg_lbl)
        self.layout.addWidget(time_lbl, 0, Qt.AlignmentFlag.AlignRight)
        
        self.setMaximumWidth(400)

class ChatWidget(QWidget):
    def __init__(self, current_user="Admin"):
        super().__init__()
        self.chat_model = Chat()
        self.current_user = current_user
        self.last_message_count = 0
        self.setup_ui()
        
        # Poll for new messages every 3 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_messages)
        self.timer.start(3000)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("5 ST★R Support Chat")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1c2833;")
        header.addWidget(title)
        header.addStretch()
        
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("color: #7f8c8d; border: none; font-size: 12px;")
        clear_btn.clicked.connect(self.clear_chat)
        header.addWidget(clear_btn)
        layout.addLayout(header)
        
        # Scroll Area for Messages
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: #f1f2f6; border: 1px solid #dcdde1; border-radius: 10px;")
        
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.addStretch()
        self.scroll.setWidget(self.message_container)
        layout.addWidget(self.scroll)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type your message here...")
        self.msg_input.setStyleSheet("""
            padding: 12px; 
            border-radius: 20px; 
            border: 1px solid #dcdde1; 
            background: white;
            font-size: 14px;
        """)
        self.msg_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            background-color: #2ecc71; 
            color: white; 
            padding: 10px 25px; 
            border-radius: 20px; 
            font-weight: bold;
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.msg_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        self.refresh_messages()

    def send_message(self):
        text = self.msg_input.text().strip()
        if not text:
            return
            
        self.chat_model.send_message(self.current_user, text)
        self.msg_input.clear()
        self.refresh_messages()
        
        # Auto-scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def refresh_messages(self):
        messages = self.chat_model.get_messages()
        if len(messages) == self.last_message_count:
            return
            
        # Clear current layout (except stretch)
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Re-add all messages
        self.last_message_count = len(messages)
        for sender, message, timestamp in messages:
            is_self = (sender == self.current_user)
            balloon = ChatBalloon(sender, message, timestamp, is_self)
            
            row = QHBoxLayout()
            if is_self: row.addStretch()
            row.addWidget(balloon)
            if not is_self: row.addStretch()
            
            self.message_layout.insertLayout(self.message_layout.count() - 1, row)
            
    def clear_chat(self):
        if self.chat_model.clear_history():
            self.refresh_messages()
            self.last_message_count = 0
