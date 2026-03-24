import os
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.auth_widget import AuthWidget

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = AuthWidget()
        self.main_window = None
        
        self.login_window.auth_success.connect(self.start_main_app)
        self.login_window.showMaximized()

    def start_main_app(self, user_data):
        self.login_window.close()
        self.main_window = MainWindow()
        # Set user display name if needed
        self.main_window.user_label.setText(f"Welcome, {user_data['full_name']}")
        self.main_window.show()

def main():
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    os.makedirs("gui", exist_ok=True)
    
    # Create __init__.py files
    for directory in ["models", "utils", "gui"]:
        init_fh = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_fh):
            with open(init_fh, "w") as f:
                pass
    
    controller = AppController()
    sys.exit(controller.app.exec())

if __name__ == "__main__":
    main()
 