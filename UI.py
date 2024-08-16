
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout, QScrollArea, \
    QLineEdit, QLabel, QCheckBox, QComboBox, QTableWidgetItem, QHeaderView, QAbstractItemView
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


        # central table widget
        self.resultBar = QLabel()
        self.tableWidget = QTableWidget()


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

        # Create buttons



        # Create bottom buttons
        self.searchBtn = QPushButton('Search')
        self.prevBtn = QPushButton('<-')
        self.nextBtn = QPushButton('->')
        self.downloadBtn = QPushButton('Download')
        # modifications to bottom layout and its buttons

        # add bottom buttons to layout
        self.bottomLayout.addWidget(self.searchBtn)
        self.bottomLayout.addWidget(self.prevBtn)
        self.bottomLayout.addWidget(self.nextBtn)
        self.bottomLayout.addWidget(self.downloadBtn)
            # bind button functions
        self.searchBtn.clicked.connect(self.search)
        self.downloadBtn.clicked.connect(self.download)


        # other settings
        self.initTable()

        # add everything to layouts
        self.topscrollarea.setLayout(self.searchBarLayout)
        self.mainLayout.addWidget(self.topscrollarea, stretch=30)
        self.mainLayout.addWidget(self.resultBar,stretch=2)
        self.mainLayout.addWidget(self.tableWidget, stretch=58)
        self.mainLayout.addLayout(self.bottomLayout, stretch=10)

        # end
        # self.mainLayout.stretch(20,50,10)
        # self.mainLayout.addStretch()
        self.setLayout(self.mainLayout)

        # testing purposes
        self.count = 1

    def initTable(self):
        self.tableWidget.setAutoScroll(False)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def search(self):
        # control buttons
        self.downloadBtn.setEnabled(True)
        self.downloader = Downloader()  # 1 new downloader per search ?
        # load params
        # primary
        self.downloader.setStudyTitle(self.titleLine.text())
        self.downloader.setCondition(self.condLine.text())
        self.downloader.setTreat(self.treatLine.text())
        self.downloader.setTerm(self.termLine.text())

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

        result = self.downloader.search()

        #TODO: add functions ?
        self.buildtable(result)


    def buildtable(self,result):
        """
        build central table with study names
        :param studies:
        :return:
        """
        print('Building Table')
        # columns:
        # checkbox, index number, study title
        count = result['count']
        studies = result['studies']

        self.tableWidget.clearContents()
        print(self.tableWidget.rowCount())
        print(self.tableWidget.columnCount())

        if len(studies) == 0:
            return

        self.resultBar.setText('Number of results: {}'.format(count))

        # TODO: change row and column numbers dynamically
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderItem(0,QTableWidgetItem('Title'))
        self.tableWidget.setRowCount(len(studies))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)



        print(f'studylength:{len(studies)}')
        for i in range(0, len(studies)):
            checkbox = QTableWidgetItem()
            # print(studies[i].title)
            checkbox.setText(studies[i].title)
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox.setCheckState(Qt.Checked)

            # self.tableWidget.removeCellWidget()
            self.tableWidget.setItem(i, 0, checkbox)



            # self.tableWidget.setItem(i,1,QTableWidgetItem(studies[i].title))
        self.count += 1
        print('Finished Building Table')

    def download(self):
        # get which file should be downloaded
        print('will download')
        self.downloadBtn.setEnabled(False)

        # a better way to do this ?
        studyindex = []
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.item(row,0)
            if checkbox.checkState() == Qt.Checked:
                studyindex.append(row)

        self.downloader.download(studyindex)
        return

    # links buttons





