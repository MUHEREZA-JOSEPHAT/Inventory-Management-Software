import os
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    os.makedirs("gui", exist_ok=True)
    
    # Create __init__.py files
    for directory in ["models", "utils", "gui"]:
        with open(f"{directory}/__init__.py", "w") as f:
            pass
    
    # Create and run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 