import os

from PySide6 import QtWidgets
import configparser

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, \
    QFormLayout


class OptionsWindow(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__()
        self.parent = parent
        self.config = config

        self.setFixedWidth(600)
        self.setWindowTitle('Options')
        self.setWindowIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))

        self.outLayout = QVBoxLayout()
        self.outLayout2 = QFormLayout()
        self.outLayout2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.layout2 = QHBoxLayout()  # for folder
        self.layout4 = QHBoxLayout()  # for folder
        self.layout3 = QHBoxLayout() # pageSize
        self.layoutLast = QHBoxLayout()  # for Yes/No buttons

        self.folder = self.parent.config_values.get('downloadFolder')
        self.pageSize = self.parent.config_values.get('pageSize')

        # select folder
        self.label1 = QLabel('Download Location:')
        self.label2 = QLineEdit(f'{self.folder}')
        self.tmpfldrstr = self.label2.text()
        self.label2.textChanged.connect(self.updatetmpstr)
        self.fldrbtn = QPushButton('Select Folder')
        self.fldrbtn.clicked.connect(self.setfolderpath)
        self.fldrbtn2 = QPushButton('Default')
        self.fldrbtn2.clicked.connect(self.setDefaultFolder)


        self.layout2.addWidget(self.label2,60)
        self.layout2.addWidget(self.fldrbtn, 20)
        self.layout2.addWidget(self.fldrbtn2, 20)

        self.outLayout2.addRow(self.label1, self.layout2)

        # change page size
        self.label3 = QLabel('Max results per page:')
        self.label4 = QLineEdit(f'{self.pageSize}')
        self.label4.textChanged.connect(self.updatePageSize)
        # self.placeholder3 = QLabel('')
        # self.layout3.addWidget(self.label3,20)
        # self.layout3.addWidget(self.label4,20)
        # self.layout3.addWidget(self.placeholder3,60)
        self.outLayout2.addRow(self.label3, self.label4)

        # bottom buttons
        self.placeholder1 = QLabel('')
        self.placeholder2 = QLabel('')
        self.btnok = QPushButton('OK')
        self.btncancel = QPushButton('Cancel')
        self.btnok.clicked.connect(self.updateConfigs)
        self.btncancel.clicked.connect(self.cancel)
        self.layoutLast.addWidget(self.placeholder1, 25)
        self.layoutLast.addWidget(self.btnok, 25)
        self.layoutLast.addWidget(self.btncancel, 25)
        self.layoutLast.addWidget(self.placeholder2, 25)


        self.outLayout.addLayout(self.outLayout2)
        self.outLayout.addLayout(self.layoutLast)
        self.setLayout(self.outLayout)

    def setfolderpath(self):
        self.folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.label2.setText(self.folder)

    def setDefaultFolder(self):
        currdir = os.getcwd()
        self.folder = os.path.join(currdir, 'download')
        self.label2.setText(self.folder)

    def updatePageSize(self):
        self.pageSize = self.label4.text()
    def updatetmpstr(self):
        # print('updatetmpstr called')
        self.folder = self.label2.text()

    def updateConfigs(self):
        # print(type(self.config))
        self.config['Options'] = {
            'Download Folder': self.folder,
            'PageSize': self.pageSize
        }
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        # print('----- from options -----')
        # print(self.folder)
        # print(self.pageSize)

        self.parent.updateConfig()
        self.close()

    def cancel(self):
        self.close()
