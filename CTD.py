from PySide6.QtWidgets import QApplication
import sys
from UI import MainWindow

if __name__ == '__main__':
    app = QApplication()
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# for pyinstaller:
# --windowed or -w : no console
# --onefile or -F for one exe file
# pyi-makespec -w -F CTD.py
# pyinstaller CTD.spec
#    datas=[
#         ('resources/indexTemplate.html','resources/indexTemplate.html'),
#         ('resources/QSS','resources/QSS')
#     ],
# currently not packing resource files. Running from temp folder may require admin rights
# pyinstaller -w --onefile --add-data="resources/QSS";"resources/QSS“ CTD.py
