
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QSize, QThreadPool, Slot
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout, QScrollArea, \
    QLineEdit, QLabel, QCheckBox, QTableWidgetItem, QAbstractItemView, QProgressBar, \
    QSizePolicy
from Downloader import Downloader
from Study import Study

class CTDWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1244, 700)
        self.setWindowTitle('CTD')
        self.setWindowIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))

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

            # other search params
                # has sap
        self.protLayout = QHBoxLayout()
        self.protbox = QCheckBox('Study Protocols')
        self.sapbox = QCheckBox('Statistical analysis plans (SAPs)')
        self.icfbox = QCheckBox('Informed consent forms (ICFs)')
        self.protbox.setChecked(True)   # by default must contain protocol
        self.protLayout.addWidget(self.protbox)
        self.protLayout.addWidget(self.sapbox)
        self.protLayout.addWidget(self.icfbox)
        self.searchBarLayout.addRow('Study Documents',self.protLayout)
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

        self.searchBarLayout.addRow('Study Phase:',self.phaseLayout)
        self.searchBarLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # result bar under the search section
        self.resultBarLayout = QHBoxLayout()
        self.resultBarLayoutLeft = QHBoxLayout()
        self.resultBarLayoutRight = QHBoxLayout() # placeholder
        self.resultBarPlaceholder = QWidget()
        self.resultBarLayoutRight.addWidget(self.resultBarPlaceholder)
        self.resultBarLabel = QLabel('Number of results:')
        self.resultBarLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.resultBarLabel.setFixedWidth(150) # by pixels
        self.resultBarProgression = QProgressBar()
        self.resultBarLayoutLeft.addWidget(self.resultBarLabel,20)
        self.resultBarLayoutLeft.addWidget(self.resultBarProgression,70)
        self.resultBarLayout.addLayout(self.resultBarLayoutLeft,50)
        self.resultBarLayout.addLayout(self.resultBarLayoutRight,50)


        # central table widget
        self.tableWidget = QTableWidget()

        ########## Create buttons ##########

        # result bar buttons
        self.resultBarStopBtn = QPushButton('Stop')
        self.resultBarLayoutLeft.addWidget(self.resultBarStopBtn,10)

        # Create bottom buttons
        self.searchBtn = QPushButton('Search')
        self.newSearchBtn = QPushButton('New Search') # just to be safe
        self.prevBtn = QPushButton('<-')
        self.nextBtn = QPushButton('->')
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
        self.initTable()

        # add everything to outermost layouts
        self.topscrollarea.setLayout(self.searchBarLayout)
        self.mainLayout.addWidget(self.topscrollarea, stretch=30)
        self.mainLayout.addLayout(self.resultBarLayout,stretch=2)
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
        self.tableWidget.setAutoScroll(False)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def search(self):
        # Need a function to handle all args/all fields
        # control buttons

        # Disable search to not lose the prev results.
        # Handle buttons first before any signals
        self.searchBtn.setEnabled(False)
        self.newSearchBtn.setEnabled(True)
        self.nextBtn.setEnabled(True)
        self.downloadBtn.setEnabled(True)

        self.downloader = Downloader()  # 1 new downloader per search ?
        self.resultBarStopBtn.pressed.connect(self.downloader.kill)
        # load params
        # primary
        self.downloader.setStudyTitle(self.titleLine.text())
        self.downloader.setCondition(self.condLine.text())
        self.downloader.setTreat(self.treatLine.text())
        self.downloader.setTerm(self.termLine.text())
        # Bind signals
        self.downloader.signals.updateProgressBar.connect(self.updateProgressBar)
        self.downloader.signals.updateDownloadButton.connect(self.updateDownloadButton)
        self.downloader.signals.disableNextBtn.connect(self.disableNextBtn)
        # Testing Params
        self.downloader.setPageSize(10)

        # aggFilters
        # TODO: separate each aggFilter into functions
            # check for protocols
        studydocuments='docs:'
        first = True
        if self.protbox.isChecked():
            tmp = 'prot' if first else ' prot'
            studydocuments+= tmp
            first = False
        if self.sapbox.isChecked():
            tmp = 'sap' if first else ' sap'
            studydocuments += tmp
            first = False
        if self.icfbox.isChecked():
            tmp = 'icf' if first else ' icf'
            studydocuments += tmp
            first = False

        self.downloader.buildAggFilters(studydocuments)
            # check for phase
        phase = 'phase:'
        phasestr=''
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
        result = self.downloader.search(pageNum=self.pageNum)

        #TODO: add functions ?
        self.buildtable(result)



    def buildtable(self, result):

        print('Building Table')
        # columns: study title
        studies = result['studies']
        indices = result['indices']

        self.tableWidget.clearContents()
        print(self.tableWidget.rowCount())
        print(self.tableWidget.columnCount())

        studylen = len(studies)
        if studylen == 0:
            return

        self.resultBarLabel.setText('Number of results: {}'.format(self.downloader.resultTotal))

        # TODO: change row and column numbers dynamically
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderItem(0,QTableWidgetItem('Title'))
        self.tableWidget.setRowCount(studylen)

        header = self.tableWidget.horizontalHeader()
        header.setDefaultSectionSize(1200)
        # header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        for i in range(0, studylen):
            checkbox = QTableWidgetItem()
            # print(studies[i].title)
            checkbox.setText(studies[i].title)
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if indices[i] == 1:
                checkbox.setCheckState(Qt.Checked)
            else:
                checkbox.setCheckState(Qt.Unchecked)

            # self.tableWidget.removeCellWidget()
            self.tableWidget.setItem(i, 0, checkbox)
            self.tableWidget.resizeRowToContents(i)

            # self.tableWidget.setItem(i,1,QTableWidgetItem(studies[i].title))
            # + (self.pageNum - 1) * self.downloader.pageSize
        self.count += 1 # for Testing Purpose

        print('Finished Building Table')

    def download(self):
        # get which file should be downloaded
        print('Dowloading...')
        self.downloadBtn.setEnabled(False)

        # Set downloader search args to generate HTML folder
        self.downloader.studyTitle = self.titleLine.text()
        self.downloader.condition = self.condLine.text()
        self.downloader.treat = self.treatLine.text()
        self.downloader.term = self.termLine.text()

        # a better way to do this ? Create a function ?
        self.downloader.updateStudyIndices(self.getCurTableState(), self.pageNum)

        self.threadpool.start(self.downloader.download)

    def updateProgressBar(self,value):
        self.resultBarProgression.setValue(value)
    def updateDownloadButton(self,bool):
        self.downloadBtn.setEnabled(bool)

    def prevPage(self):
        # record current state
        print(f'1st line prevPage pageNum: {self.pageNum}')
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
        print('Prev Page')
        print(result['indices'])
        print('study indices:')
        print(self.downloader.studyIndices)
        print('prevPage ends')
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
        print('Next Page')
        print(f'currPageNum:{self.pageNum}')
        print(result['indices'])
        print(self.downloader.studyIndices)
        print('nextPage ends\n\n')
    def newSearch(self):
        self.searchBtn.setEnabled(True)
        self.newSearchBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)
        return

    def disableNextBtn(self,bool):
        print(f'SIGNAL RECEIVED: {bool}')
        self.nextBtn.setEnabled(bool)

    def getCurTableState(self):
        studyIndices = []
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.item(row,0)
            if checkbox.checkState() == Qt.Checked:
                studyIndices.append(1)
            else:
                studyIndices.append(0)
        return studyIndices
