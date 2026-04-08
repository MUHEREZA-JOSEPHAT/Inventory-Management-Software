from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QScrollArea, QFrame, QWidget, QSplitter,
    QMessageBox, QSizePolicy, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from datetime import datetime
import json
import os
from models.supplier_communication import SupplierCommunication

class EmailSenderWorker(QThread):
    finished = pyqtSignal(bool, str) # success, error_message
    
    def __init__(self, email_service, supplier_email, subject, message, attachments=None):
        super().__init__()
        self.email_service = email_service
        self.supplier_email = supplier_email
        self.subject = subject
        self.message = message
        self.attachments = attachments or []
        
    def run(self):
        success, error = self.email_service.send_email(
            self.supplier_email, self.subject, self.message, self.attachments
        )
        self.finished.emit(success, error if not success else "")

class MessageBalloon(QFrame):
    def __init__(self, text, sender_type, timestamp, attachments=None):
        super().__init__()
        self.attachments = attachments or []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        is_admin = sender_type == "Admin"
        
        # Modern Balloon styling
        # Admin: Vivid Blue with White text | Supplier: Light Grey with Dark text
        bg_color = "#1a73e8" if is_admin else "#f1f3f4"
        text_color = "white" if is_admin else "#202124"
        meta_color = "#e8f0fe" if is_admin else "#5f6368"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 18px;
                border: none;
            }}
        """)
        
        msg_label = QLabel(text)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {text_color}; font-size: 14px; border: none; background: transparent; font-family: 'Inter', 'Segoe UI';")
        
        time_label = QLabel(f"{timestamp}")
        time_label.setStyleSheet(f"color: {meta_color}; font-size: 10px; border: none; background: transparent;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight if is_admin else Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(msg_label)
        
        # Attachment Display inside the bubble
        if self.attachments:
            attach_container = QWidget()
            attach_container.setStyleSheet("background: transparent; border: none;") # Force transparency
            attach_layout = QVBoxLayout(attach_container)
            attach_layout.setContentsMargins(0, 5, 0, 5)
            attach_layout.setSpacing(5)
            
            # Use a slightly more distinct overlay for files
            chip_bg = "rgba(255, 255, 255, 0.25)" if is_admin else "rgba(0, 0, 0, 0.08)"
            chip_hover = "rgba(255, 255, 255, 0.35)" if is_admin else "rgba(0, 0, 0, 0.12)"

            for path in self.attachments:
                name = os.path.basename(path)
                btn = QPushButton(f"  📄 {name}")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {chip_bg};
                        color: {text_color};
                        border: 1px solid {"rgba(255,255,255,0.4)" if is_admin else "rgba(0,0,0,0.15)"};
                        border-radius: 10px;
                        padding: 6px 12px;
                        text-align: left;
                        font-size: 12px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {chip_hover};
                    }}
                """)
                btn.clicked.connect(lambda checked, p=path: self._open_file(p))
                attach_layout.addWidget(btn)
            
            layout.addWidget(attach_container)

        layout.addWidget(time_label)
        
        self.setMaximumWidth(480)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def _open_file(self, path):
        try:
            if os.path.exists(path):
                os.startfile(path)
            else:
                QMessageBox.warning(self, "File Not Found", f"The original file at '{path}' could not be located.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

class SupplierEmailDialog(QDialog):
    def __init__(self, supplier_id, supplier_name, supplier_email, parent=None, initial_attachments=None):
        super().__init__(parent)
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.supplier_email = supplier_email
        self.comm_model = SupplierCommunication()
        self.attachments = initial_attachments if initial_attachments else []
        
        self.setWindowTitle(f"Email Exchange: {supplier_name}")
        self.setMinimumSize(700, 600)
        
        self.setup_ui()
        self.comm_model.mark_as_read(self.supplier_id)
        self.refresh_history()
        
        # If we have initial attachments, update the tray immediately
        if self.attachments:
            self.update_tray()
            self.subject_edit.setText(f"New Order: 5 STAR SUPERMARKET - {datetime.now().strftime('%d/%m/%Y')}")
        
        # Timer 1: Refresh UI from local database every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_history)
        self.timer.start(5000)
        
        # Timer 2: Sync with remote IMAP server every 60 seconds (background polling)
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(lambda: self.comm_model.sync_incoming_emails(self.supplier_id))
        self.sync_timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header Info
        header = QFrame()
        header.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 10px;")
        h_layout = QHBoxLayout(header)
        
        info_label = QLabel(f"📧 <b>To:</b> {self.supplier_name} ({self.supplier_email})")
        info_label.setStyleSheet("font-size: 14px;")
        h_layout.addWidget(info_label)
        
        # Sync mail button
        sync_btn = QPushButton("🔃 Check for New Mail")
        sync_btn.setStyleSheet("background: #1a73e8; color: white; padding: 5px 12px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        sync_btn.clicked.connect(self.check_new_mail)

        # Simulate reply button for demo
        sim_btn = QPushButton("🧪 Simulate Supplier Reply")
        sim_btn.setStyleSheet("background: #5f6368; color: white; padding: 5px 12px; border-radius: 4px; font-size: 11px;")
        sim_btn.clicked.connect(self._simulate_reply)
        
        h_layout.addStretch()
        h_layout.addWidget(sync_btn)
        h_layout.addWidget(sim_btn)
        
        layout.addWidget(header)
        
        # Message History Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: white;")
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.addStretch()
        self.scroll.setWidget(self.history_container)
        
        layout.addWidget(self.scroll, 1)
        
        # Compose Area
        compose_box = QFrame()
        compose_box.setStyleSheet("border-top: 1px solid #dadce0; padding-top: 10px;")
        c_layout = QVBoxLayout(compose_box)
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Subject Line...")
        self.subject_edit.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px;")
        
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Type your email here...")
        self.message_edit.setMaximumHeight(120)
        self.message_edit.setStyleSheet("padding: 8px; border-radius: 4px;")
        
        # Attachment Tray (Shows selected files)
        self.tray_widget = QWidget()
        self.tray_layout = QHBoxLayout(self.tray_widget)
        self.tray_layout.setContentsMargins(0, 5, 0, 5)
        self.tray_widget.hide()
        
        btn_layout = QHBoxLayout()
        self.attach_btn = QPushButton("📎 Attach Files")
        self.attach_btn.setStyleSheet("background-color: #f1f3f4; color: #5f6368; padding: 8px 15px; border-radius: 4px; border: 1px solid #dadce0;")
        self.attach_btn.clicked.connect(self.attach_files)

        self.send_btn = QPushButton("🚀 Send Email")
        self.send_btn.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px 25px; font-weight: bold; border-radius: 4px;")
        self.send_btn.clicked.connect(self.send_email)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        btn_layout.addWidget(self.status_label)
        btn_layout.addStretch()
        btn_layout.addWidget(self.attach_btn)
        btn_layout.addWidget(self.send_btn)
        
        c_layout.addWidget(self.subject_edit)
        c_layout.addWidget(self.message_edit)
        c_layout.addWidget(self.tray_widget)
        c_layout.addLayout(btn_layout)
        
        layout.addWidget(compose_box)

    def refresh_history(self):
        # Clear existing
        from PyQt6 import sip
        while self.history_layout.count() > 1:
            child = self.history_layout.takeAt(0)
            if child.widget():
                sip.delete(child.widget())
        
        self.history_layout.setSpacing(15)
        
        history = self.comm_model.get_communication_history(self.supplier_id)
        for sender, subject, msg, timestamp, status, att_json in history:
            # Parse attachments from JSON
            attachments = []
            if att_json:
                try:
                    attachments = json.loads(att_json)
                except:
                    attachments = []
                    
            balloon = MessageBalloon(msg, sender, timestamp, attachments)
            # Create a horizontal wrapper for alignment
            wrapper = QHBoxLayout()
            wrapper.setContentsMargins(0, 0, 0, 0)
            
            if sender == "Admin":
                wrapper.addStretch()
                wrapper.addWidget(balloon)
            else:
                wrapper.addWidget(balloon)
                wrapper.addStretch()
                
            self.history_layout.insertLayout(self.history_layout.count() - 1, wrapper)
            
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))
        
        # Ensure status label exists if not already added (safety)
        if not hasattr(self, 'status_label'):
             self.status_label = QLabel("")

    def send_email(self):
        subject = self.subject_edit.text().strip()
        message = self.message_edit.toPlainText().strip()
        
        if not message:
            return
            
        if not subject:
            subject = "Follow-up regarding Supply Order"
            
        # UI State: Loading
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Sending.....")
        self.status_label.setText("⏳ Dispatching email...")
        self.status_label.setStyleSheet("color: #5f6368; font-weight: bold;")
        
        # Launch background worker
        # We need the service which is currently in the comm_model or window
        # For simplicity, we'll use the email_service if available
        from services.email_service import EmailService
        service = EmailService()
        
        # Start worker with attachments
        self.worker = EmailSenderWorker(service, self.supplier_email, subject, message, self.attachments)
        self.worker.finished.connect(lambda success, err: self._on_email_finished(success, err, subject, message))
        self.worker.start()

    def _on_email_finished(self, success, error, subject, message):
        """Handles the callback from the background email thread"""
        self.send_btn.setEnabled(True)
        self.send_btn.setText("🚀 Send Email")
        
        if success:
            # UI State: Success
            self.status_label.setText("✅ Sent Successfully")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            # Log communication (Include attachments)
            self.comm_model.log_communication(
                self.supplier_id, "Admin", "Admin", 
                self.supplier_email, subject, message, "Sent", 
                attachments=self.attachments
            )
            
            # Reset UI
            self.message_edit.clear()
            self.attachments = []
            self.update_tray()
            self.refresh_history()
            
            # Auto-clear status after 5 seconds
            QTimer.singleShot(5000, lambda: self.status_label.setText(""))
        else:
            # UI State: Failed
            self.status_label.setText("❌ Failed to Send")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.critical(self, "Email Dispatch Failed", f"Could not reach mail server:\n\n{error}")
            QTimer.singleShot(10000, lambda: self.status_label.setText(""))

    def _simulate_reply(self):
        self.comm_model.simulate_supplier_reply(self.supplier_id)
        self.refresh_history()

    def check_new_mail(self):
        """Manually trigger a sync of incoming emails"""
        count = self.comm_model.sync_incoming_emails(self.supplier_id)
        if count > 0:
            self.refresh_history()
            QMessageBox.information(self, "Mail Sync", f"Found {count} new message(s) from this supplier!")
        else:
            QMessageBox.information(self, "Mail Sync", "No new messages found from this supplier in your inbox.")

    def attach_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Attach")
        if files:
            for f in files:
                if f not in self.attachments:
                    self.attachments.append(f)
            self.update_tray()

    def update_tray(self):
        # Clear tray
        import os
        from PyQt6 import sip
        while self.tray_layout.count() > 0:
            item = self.tray_layout.takeAt(0)
            if item.widget():
                sip.delete(item.widget())
        
        if not self.attachments:
            self.tray_widget.hide()
            return
            
        self.tray_widget.show()
        for path in self.attachments:
            chip = QFrame()
            chip.setStyleSheet("background: #e8f0fe; border-radius: 12px; padding: 2px 8px; border: 1px solid #d2e3fc;")
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(5, 2, 5, 2)
            
            name = os.path.basename(path)
            label = QLabel(f"📄 {name}")
            label.setStyleSheet("font-size: 11px; color: #1a73e8; border: none;")
            
            rem_btn = QPushButton("✕")
            rem_btn.setFixedSize(16, 16)
            rem_btn.setStyleSheet("background: transparent; border: none; font-weight: bold; color: #5f6368; cursor: pointer;")
            rem_btn.clicked.connect(lambda checked, p=path: self.remove_attachment(p))
            
            chip_layout.addWidget(label)
            chip_layout.addWidget(rem_btn)
            self.tray_layout.addWidget(chip)
            
        self.tray_layout.addStretch()

    def remove_attachment(self, path):
        if path in self.attachments:
            self.attachments.remove(path)
            self.update_tray()
