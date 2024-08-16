from PySide6.QtWidgets import QApplication
import sys
from UI import CTDWindow
import re

if __name__ == '__main__':
    app = QApplication()
    window = CTDWindow()
    window.show()
    sys.exit(app.exec())