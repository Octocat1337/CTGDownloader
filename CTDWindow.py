import os
from math import ceil, floor

from PySide6 import QtCore
from PySide6.QtCore import Qt, QThreadPool, Slot
from PySide6.QtGui import QIcon, QFont, QStandardItem

from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout, QScrollArea, \
    QLineEdit, QLabel, QCheckBox, QTableWidgetItem, QAbstractItemView, QProgressBar, \
    QSizePolicy, QMessageBox, QMainWindow, QHeaderView
from Downloader import Downloader

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p',
                    filename='CTD-log.log', encoding='utf-8', level=logging.INFO)


class CTDWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # args from children: downloader.HTMLWriter
        self.downloadFolderName = ''
        self.parent = parent
        # Setup Style Sheet
        filename = os.path.join('resources', 'QSS')
        with open(filename, 'r') as f:
            self.setStyleSheet(f.read())

        # Setup logger
        logger.info('-----New Instance Started-----')

        # Outtermost main layout
        self.mainLayout = QVBoxLayout()
        self.topscrollarea = QScrollArea()
        self.searchBarLayout = QFormLayout()

        self.bottomLayout = QHBoxLayout()

        # top search bar, will expand
        # self.topscrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.titleLabel = QLabel('Title')
        self.titleLine = QLineEdit()
        self.searchBarLayout.addRow(self.titleLabel, self.titleLine)

        self.condLabel = QLabel('Condition')
        self.condLine = QLineEdit()
        self.searchBarLayout.addRow(self.condLabel, self.condLine)

        self.treatLabel = QLabel('Intervention/treatment')
        self.treatLine = QLineEdit()
        self.searchBarLayout.addRow(self.treatLabel, self.treatLine)

        self.termLabel = QLabel('Other terms')
        self.termLine = QLineEdit()
        self.searchBarLayout.addRow(self.termLabel, self.termLine)

        self.sponsorLabel = QLabel('Sponsor')
        self.sponsorLine = QLineEdit()
        self.searchBarLayout.addRow(self.sponsorLabel, self.sponsorLine)

        # other search params
        # has sap
        self.protLayout = QHBoxLayout()
        self.protbox = QCheckBox('Study Protocols')
        self.sapbox = QCheckBox('Statistical analysis plans (SAPs)')
        self.icfbox = QCheckBox('Informed consent forms (ICFs)')
        self.protbox.setChecked(True)  # by default must contain protocol
        self.protLayout.addWidget(self.protbox)
        self.protLayout.addWidget(self.sapbox)
        self.protLayout.addWidget(self.icfbox)
        self.searchBarLayout.addRow('Study Documents', self.protLayout)
        # Study phase
        self.phaseLayout = QHBoxLayout()
        self.phase0box = QCheckBox('Early Phase 1')
        self.phase1box = QCheckBox('Phase 1')
        self.phase2box = QCheckBox('Phase 2')
        self.phase3box = QCheckBox('Phase 3')
        self.phase4box = QCheckBox('Phase 4')
        self.phasenabox = QCheckBox('Not Applicable')
        self.phaseLayout.addWidget(self.phase0box)
        self.phaseLayout.addWidget(self.phase1box)
        self.phaseLayout.addWidget(self.phase2box)
        self.phaseLayout.addWidget(self.phase3box)
        self.phaseLayout.addWidget(self.phase4box)
        self.phaseLayout.addWidget(self.phasenabox)

        self.searchBarLayout.addRow('Study Phase', self.phaseLayout)
        self.searchBarLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # result bar under the search section
        self.resultBarLayout = QHBoxLayout()
        self.resultBarLayoutLeft = QHBoxLayout()
        self.resultBarLayoutRight = QHBoxLayout()

        self.resultBarLabel = QLabel('Number of results:')
        self.resultBarLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.resultBarLabel.setFixedWidth(150)  # by pixels
        self.pageNumLabel = QLabel('Page:')
        self.pageNumLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pageNumLabel.setFixedWidth(80)  # by pixels
        self.resultBarProgression = QProgressBar()

        self.resultBarLayoutLeft.addWidget(self.resultBarLabel, 20)
        self.resultBarLayoutLeft.addWidget(self.pageNumLabel, 5)
        self.resultBarLayoutLeft.addWidget(self.resultBarProgression, 60)

        self.resultBarLayout.addLayout(self.resultBarLayoutLeft, 60)
        self.resultBarLayout.addLayout(self.resultBarLayoutRight, 40)

        # central table widget
        self.tableHeader1 = None
        self.tableWidget = QTableWidget()

        ########## Create buttons ##########

        # result bar buttons
        self.resultBarStopBtn = QPushButton('Stop')
        self.resultBarLayoutLeft.addWidget(self.resultBarStopBtn, 10)
        self.dlAllBtn = QPushButton('Download All')
        self.dlAllBtn.clicked.connect(self.downloadAll)
        self.dlAllBtn.setEnabled(False)
        self.resultBarLayoutRight.addWidget(self.dlAllBtn, 20)
        self.dlFldrBtn = QPushButton('Open Download Folder')
        self.dlFldrBtn.setEnabled(False)
        self.resultBarLayoutRight.addWidget(self.dlFldrBtn, 20)
        self.placeholder = QLabel('')
        self.resultBarLayoutRight.addWidget(self.placeholder, 60)

        # Create bottom buttons
        self.searchBtn = QPushButton('Search')
        self.newSearchBtn = QPushButton('New Search')  # just to be safe
        self.prevBtn = QPushButton('<< Prev Page')
        self.nextBtn = QPushButton('Next Page >>')
        self.downloadBtn = QPushButton('Download')
        # modifications to bottom layout and its buttons

        # add bottom buttons to layout
        self.bottomLayout.addWidget(self.searchBtn)
        self.bottomLayout.addWidget(self.newSearchBtn)
        self.bottomLayout.addWidget(self.prevBtn)
        self.bottomLayout.addWidget(self.nextBtn)
        self.bottomLayout.addWidget(self.downloadBtn)
        # bind button functions
        self.searchBtn.clicked.connect(self.search)
        self.newSearchBtn.clicked.connect(self.newSearch)
        self.newSearchBtn.setEnabled(False)
        self.prevBtn.clicked.connect(self.prevPage)
        self.prevBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)
        self.nextBtn.clicked.connect(self.nextPage)
        self.downloadBtn.clicked.connect(self.download)
        self.downloadBtn.setEnabled(False)

        # other settings
        # initialize central table
        self.initTable()

        # add everything to outermost layouts
        self.topscrollarea.setLayout(self.searchBarLayout)
        self.mainLayout.addWidget(self.topscrollarea, stretch=30)
        self.mainLayout.addLayout(self.resultBarLayout, stretch=2)
        # self.mainLayout.addView(self.tableWidget, stretch=58)
        self.mainLayout.addWidget(self.tableWidget, stretch=58)
        self.mainLayout.addLayout(self.bottomLayout, stretch=10)

        # end
        self.setLayout(self.mainLayout)

        # Multi-Thread Progress bar
        self.threadpool = QThreadPool()

        # testing purposes
        self.count = 1

        # page functions
        self.pageNum = 0

    def initTable(self):

        self.titlepos = 1

        self.tableWidget.setAutoScroll(False)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setColumnCount(2)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(0, 20)
        self.tableWidget.setColumnWidth(1, 1180)

        self.tableHeader1 = QTableWidgetItem()
        self.tableHeader1.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditSelectAll))

        self.tableWidget.horizontalHeader().setSectionsClickable(True)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.selectAll)
        self.tableWidget.setHorizontalHeaderItem(0, self.tableHeader1)
        self.tableWidget.setHorizontalHeaderItem(self.titlepos, QTableWidgetItem('Title'))

    def search(self):
        # Need a function to handle all args/all fields
        # control buttons

        # Disable search to not lose the prev results.
        # Handle buttons first before any signals
        self.searchBtn.setEnabled(False)
        self.newSearchBtn.setEnabled(True)
        self.nextBtn.setEnabled(True)

        self.downloader = Downloader(parent=self)  # 1 new downloader per search ?
        self.resultBarStopBtn.pressed.connect(self.stopDownload)
        # load params
        # primary
        self.downloader.setStudyTitle(self.titleLine.text())
        self.downloader.setCondition(self.condLine.text())
        self.downloader.setTreat(self.treatLine.text())
        self.downloader.setTerm(self.termLine.text())
        self.downloader.setSponsor(self.sponsorLine.text())
        # Bind signals
        self.downloader.signals.updateProgressBar.connect(self.updateProgressBar)
        self.downloader.signals.updateDownloadButton.connect(self.updateDownloadButton)
        self.downloader.signals.disableNextBtn.connect(self.disableNextBtn)
        # Testing Params

        # aggFilters
        # TODO: separate each aggFilter into functions
        # check for protocols
        studydocuments = 'docs:'
        tmp = ''
        if self.protbox.isChecked():
            tmp += ' prot'
        if self.sapbox.isChecked():
            tmp += ' sap'
        if self.icfbox.isChecked():
            tmp += ' icf'
        studydocuments += tmp.strip()

        self.downloader.buildAggFilters(studydocuments)
        # check for phase
        phase = 'phase:'
        phasestr = ''
        if self.phase0box.isChecked():
            phasestr += ' 0'
        if self.phase1box.isChecked():
            phasestr += ' 1'
        if self.phase2box.isChecked():
            phasestr += ' 2'
        if self.phase3box.isChecked():
            phasestr += ' 3'
        if self.phase4box.isChecked():
            phasestr += ' 4'
        if self.phasenabox.isChecked():
            phasestr += ' NA'
        phase += phasestr.strip()

        self.downloader.buildAggFilters(phase)

        self.pageNum = 1

        # Enable relative buttons
        self.downloadBtn.setEnabled(True)
        self.dlAllBtn.setEnabled(True)

        # build table based on resutls
        result = self.downloader.search(pageNum=self.pageNum)

        self.resultBarLabel.setText('Number of results: {}'.format(self.downloader.resultTotal))
        totalpages = ceil(self.downloader.resultTotal / self.downloader.pageSize)
        self.pageNumLabel.setText(f'Page: {self.pageNum}/{totalpages}')
        logger.info('Search Finished')

        self.buildtable(result)

    def buildtable(self, result):

        logger.info('-----Building Table-----')
        # columns: study title
        studies = result['studies']
        indices = result['indices']

        self.tableWidget.clearContents()
        # logger.info(self.tableWidget.rowCount())
        # logger.info(self.tableWidget.columnCount())
        totalpages = ceil(self.downloader.resultTotal / self.downloader.pageSize)
        self.pageNumLabel.setText(f'Page: {self.pageNum}/{totalpages}')

        studylen = len(studies)
        if studylen == 0:
            return

        # titlepos = 1
        # self.tableWidget.setColumnCount(2)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # self.tableWidget.setColumnWidth(0, 20)
        # self.tableWidget.setColumnWidth(1, 1180)
        # self.tableHeader1 = QTableWidgetItem()
        # self.tableHeader1.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditSelectAll))
        #
        # self.tableWidget.horizontalHeader().setSectionsClickable(True)
        # self.tableWidget.horizontalHeader().sectionClicked.connect(self.selectAll)
        # self.tableWidget.setHorizontalHeaderItem(0, self.tableHeader1)
        # self.tableWidget.setHorizontalHeaderItem(titlepos, QTableWidgetItem('Title'))
        self.tableWidget.setRowCount(studylen)

        # self.tableWidget.cellClicked.connect(self.selectAll)

        # header = self.tableWidget.horizontalHeader()
        # header.resizeSection(0,20)
        # header.resizeSection(titlepos,1000)
        # header.setDefaultSectionSize(1200)
        # header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        for i in range(0, studylen):
            checkbox = QTableWidgetItem()
            title = QTableWidgetItem()
            # logger.info(studies[i].title)
            title.setFont(QFont('San Francisco', 12))
            title.setText(studies[i].title)
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if indices[i] == 1:
                checkbox.setCheckState(Qt.Checked)
            else:
                checkbox.setCheckState(Qt.Unchecked)

            # self.tableWidget.removeCellWidget()
            self.tableWidget.setItem(i, self.titlepos, title)
            self.tableWidget.setItem(i, 0, checkbox)

            self.tableWidget.resizeRowToContents(i)

        self.count += 1  # for Testing Purpose

        logger.info('-----Finished Building Table-----')

    def download(self, all=False):
        # get which file should be downloaded
        logger.info('Dowloading...')
        self.downloadBtn.setEnabled(False)
        self.dlAllBtn.setEnabled(False)

        # a better way to do this ? Create a function ?
        self.downloader.updateStudyIndices(self.getCurTableState(), self.pageNum)

        if all:
            self.threadpool.start(self.downloader.downloadAll)
        else:
            self.threadpool.start(self.downloader.download)

        self.dlFldrBtn.clicked.connect(self.openDownloadFolder)
        self.dlFldrBtn.setEnabled(True)

    def downloadAll(self):
        logger.info('Download ALL button pressed')
        choice = QMessageBox.question(
            self,
            "",
            f'You will download {self.downloader.resultTotal} studies',
            defaultButton=QMessageBox.No
        )
        if choice == QMessageBox.Yes:
            self.nextBtn.setEnabled(False)
            self.prevBtn.setEnabled(False)
            self.downloadBtn.setEnabled(False)
            self.dlAllBtn.setEnabled(False)
            self.searchBtn.setEnabled(False)
            self.download(all=True)

    def updateProgressBar(self, value):
        self.resultBarProgression.setValue(value)

    def updateDownloadButton(self, bool):
        self.downloadBtn.setEnabled(bool)

    def stopDownload(self):
        self.updateProgressBar(0)
        self.prevBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)
        self.downloader.kill()

    def prevPage(self):
        # record current state
        logger.info(f'1st line prevPage pageNum: {self.pageNum}')
        self.downloader.updateStudyIndices(self.getCurTableState(), self.pageNum)
        # check if it's first page
        self.pageNum -= 1
        if self.pageNum <= 1:
            self.prevBtn.setEnabled(False)

        # update table
        result = self.downloader.search(self.pageNum)
        self.buildtable(result)
        # enable buttons
        self.nextBtn.setEnabled(True)
        logger.info('Prev Page')
        logger.info(result['indices'])
        logger.info('study indices:')
        logger.info(self.downloader.studyIndices)
        logger.info('prevPage ends')
        return

    def nextPage(self):
        # No change in search parameters
        # thus no need to get params again.

        # Step 1: record current selections
        self.downloader.updateStudyIndices(self.getCurTableState(), self.pageNum)

        # Step 2: get new results and build table
        self.pageNum += 1
        result = self.downloader.search(self.pageNum)
        self.buildtable(result)
        # Step 3: Enable prev button
        self.prevBtn.setEnabled(True)
        logger.info('Next Page')
        logger.info(f'currPageNum:{self.pageNum}')
        logger.info(result['indices'])
        logger.info(self.downloader.studyIndices)
        logger.info('nextPage ends\n')

    def newSearch(self):
        self.searchBtn.setEnabled(True)
        self.newSearchBtn.setEnabled(False)
        self.prevBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)
        # disable all download buttons
        self.downloadBtn.setEnabled(False)
        self.dlAllBtn.setEnabled(False)
        self.dlFldrBtn.setEnabled(False)
        # reset progress bar
        self.updateProgressBar(0)

    def disableNextBtn(self, bool):
        logger.warning(f'Stop button SIGNAL RECEIVED: {bool}')
        self.nextBtn.setEnabled(bool)

    def getCurTableState(self):
        studyIndices = []
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.item(row, 0)
            if checkbox.checkState() == Qt.Checked:
                studyIndices.append(1)
            else:
                studyIndices.append(0)
        return studyIndices

    @Slot()
    def openDownloadFolder(self):
        os.startfile(self.downloadFolderName)

    @Slot()
    def selectAll(self, index):
        # 1st time clicked, select none
        if index == 0:
            print('called. ')
            print(self.tableWidget.item(0,0).checkState())
            if self.tableWidget.item(0,0).checkState()==Qt.Checked:
                for row in range(self.tableWidget.rowCount()):
                    checkbox = self.tableWidget.item(row, 0)
                    checkbox.setCheckState(Qt.Unchecked)
            else:
                for row in range(self.tableWidget.rowCount()):
                    checkbox = self.tableWidget.item(row, 0)
                    checkbox.setCheckState(Qt.Checked)
