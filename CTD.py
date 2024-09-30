from PySide6.QtWidgets import QApplication
import sys
from UI import MainWindow
import re

if __name__ == '__main__':
    app = QApplication()
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())