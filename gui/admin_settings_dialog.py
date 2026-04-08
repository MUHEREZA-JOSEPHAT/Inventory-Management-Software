from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFormLayout, QFrame, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from models.supplier_communication import SupplierCommunication

class AdminSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mail API & Admin Settings")
        self.setMinimumSize(500, 450)
        self.comm_model = SupplierCommunication()
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("📧 Mail Configuration")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1c2833;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        
        # --- General Settings Tab ---
        self.general_tab = QWidget()
        gen_layout = QFormLayout(self.general_tab)
        
        self.admin_email_edit = QLineEdit()
        self.admin_email_edit.setPlaceholderText("e.g. admin@supermarket.com")
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Simulation", "SMTP", "API", "Mailgun"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        
        gen_layout.addRow("Admin Email Address:", self.admin_email_edit)
        gen_layout.addRow("Email Dispatch Mode:", self.mode_combo)
        
        self.tabs.addTab(self.general_tab, "General")

        # --- SMTP Configuration Tab ---
        self.smtp_tab = QWidget()
        smtp_layout = QFormLayout(self.smtp_tab)
        
        self.smtp_host_edit = QLineEdit()
        self.smtp_port_edit = QLineEdit()
        self.smtp_user_edit = QLineEdit()
        self.smtp_pass_edit = QLineEdit()
        self.smtp_pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        smtp_layout.addRow("SMTP Host:", self.smtp_host_edit)
        smtp_layout.addRow("SMTP Port:", self.smtp_port_edit)
        smtp_layout.addRow("SMTP User:", self.smtp_user_edit)
        smtp_layout.addRow("SMTP Password:", self.smtp_pass_edit)
        
        smtp_layout.addRow(QLabel("<b>Incoming Mail (IMAP)</b>"), QLabel(""))
        self.imap_host_edit = QLineEdit()
        self.imap_host_edit.setPlaceholderText("e.g. imap.gmail.com")
        self.imap_port_edit = QLineEdit()
        self.imap_port_edit.setPlaceholderText("993")
        
        smtp_layout.addRow("IMAP Host:", self.imap_host_edit)
        smtp_layout.addRow("IMAP Port:", self.imap_port_edit)
        
        self.tabs.addTab(self.smtp_tab, "SMTP Settings")

        # --- API Configuration Tab ---
        self.api_tab = QWidget()
        api_layout = QFormLayout(self.api_tab)
        
        self.api_endpoint_edit = QLineEdit()
        self.api_sid_edit = QLineEdit()
        self.api_sid_edit.setPlaceholderText("Optional: Account SID / Username")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your API Private Key / Secret")
        
        api_layout.addRow("API Endpoint URL:", self.api_endpoint_edit)
        api_layout.addRow("API SID / Username:", self.api_sid_edit)
        api_layout.addRow("API Private Key:", self.api_key_edit)
        
        self.tabs.addTab(self.api_tab, "REST API Settings")
        
        layout.addWidget(self.tabs)

        # Footer
        footer = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        footer.addStretch()
        footer.addWidget(save_btn)
        footer.addWidget(cancel_btn)
        layout.addLayout(footer)

    def _on_mode_changed(self, index):
        mode = self.mode_combo.currentText()
        if mode == "SMTP":
            self.tabs.setCurrentWidget(self.smtp_tab)
        elif mode == "API" or mode == "Mailgun":
            self.tabs.setCurrentWidget(self.api_tab)
        else:
            self.tabs.setCurrentWidget(self.general_tab)

    def load_settings(self):
        settings = self.comm_model.email_service.get_settings()
        if settings:
            self.admin_email_edit.setText(settings['admin_email'] or "")
            self.mode_combo.setCurrentText(settings['mail_mode'] or "Simulation")
            self.smtp_host_edit.setText(settings['smtp_host'] or "")
            self.smtp_port_edit.setText(str(settings['smtp_port'] or ""))
            self.smtp_user_edit.setText(settings['smtp_user'] or "")
            self.smtp_pass_edit.setText(settings['smtp_pass'] or "")
            self.imap_host_edit.setText(settings.get('imap_host') or "imap.gmail.com")
            self.imap_port_edit.setText(str(settings.get('imap_port') or "993"))
            self.api_endpoint_edit.setText(settings.get('api_endpoint') or "")
            self.api_sid_edit.setText(settings.get('api_sid') or "")
            self.api_key_edit.setText(settings.get('api_key') or "")

    def save_settings(self):
        try:
            port = self.smtp_port_edit.text()
            data = {
                'admin_email': self.admin_email_edit.text().strip(),
                'mail_mode': self.mode_combo.currentText(),
                'smtp_host': self.smtp_host_edit.text().strip(),
                'smtp_port': int(port) if port else 0,
                'smtp_user': self.smtp_user_edit.text().strip(),
                'smtp_pass': self.smtp_pass_edit.text().strip(),
                'imap_host': self.imap_host_edit.text().strip(),
                'imap_port': int(self.imap_port_edit.text().strip() or 993),
                'api_endpoint': self.api_endpoint_edit.text().strip(),
                'api_sid': self.api_sid_edit.text().strip(),
                'api_key': self.api_key_edit.text().strip(),
            }
            if self.comm_model.update_admin_email_settings(**data):
                QMessageBox.information(self, "Success", "Mail settings updated successfully!")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")
