import os

from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, QAction

import configparser
import CTDWindow
import Options
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p',
                    filename='CTD-log.log', encoding='utf-8', level=logging.INFO)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1244, 700)
        self.setWindowTitle('CTD')
        self.setWindowIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))

        self.ctdwindow = CTDWindow.CTDWindow(parent=self)
        self.setCentralWidget(self.ctdwindow)

        # add options menu
        menu = self.menuBar()
        file_menu = menu.addMenu('File')

        options = QAction(self)
        options.setText('Options')
        options.triggered.connect(self.openOptionsMenu)
        options.setCheckable(False)
        file_menu.addAction(options)

        self.optionsWindow = None
        self.config_values = None

        currdir = os.getcwd()
        defaultDownloadFolder = os.path.join(currdir, 'download')
        # Setup configs from config file
        self.config = configparser.ConfigParser()
        if not os.path.exists('config.ini'):
            self.config['Options'] = {
                'Download Folder': f'{defaultDownloadFolder}',
                'PageSize': '10'
            }
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
        self.updateConfig()


    def openOptionsMenu(self):
        self.optionsWindow = Options.OptionsWindow(parent=self,config=self.config)
        self.optionsWindow.show()

    def updateConfig(self):
        """
            re-read the config file
        :return:
        """
        self.config.read('config.ini')
        downloadFolder = self.config['Options']['Download Folder']
        pageSize = int(self.config['Options']['PageSize'])

        self.config_values = {
            'downloadFolder': downloadFolder,
            'pageSize': pageSize
        }

