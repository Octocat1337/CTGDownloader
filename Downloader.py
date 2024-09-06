import csv
from enum import Enum
import os.path
import urllib3
from PySide6 import QtCore
from PySide6.QtCore import QRunnable, Signal, Slot, QObject

from HTMLWriter import HTMLWriter
from Study import Study
import re
from datetime import datetime


# for multi-thread
class WorkerSignal(QObject):
    def __init__(self):
        super().__init__()

    updateProgressBar = Signal(int)
    updateDownloadButton = Signal(bool)
    disableNextBtn = Signal(bool)


class WorkerKilledException(Exception):
    pass


class Downloader(QRunnable):
    class SecondaryAPI(Enum):
        studies = '/studies'
        nctID = '/studies/'
        metadata = '/studies/metadata'

        def __str__(self):
            return str(self.value)

    def __init__(self, filemode='HTML'):
        super().__init__()
        self.defaulturl = 'https://clinicaltrials.gov/api/v2'
        self.downloadFolder = './download'
        self.secondaryAPI = str(self.SecondaryAPI.studies)
        self.downloadurl = ''
        self.fields = 'Study Title|Study Documents'
        self.format = 'csv'
        # Multi-Thread for the progress bar
        self.signals = WorkerSignal()
        self.is_killed = False
        self.indexToDownload = []  # [index of studies to download]

        # optional search args
        self.studyTitle = ''
        self.outcome = ''  # outcome

        # displayed on the front page of website
        self.condition = ''
        self.term = ''  # other terms
        self.treat = ''  # treatment
        self.location = ''  # location , cannot do. use google map api ?

        # aggFilters
        self.aggFilters = ''
        self.phase = ''  # 0 1 2 3 4 NA

        # functional args
        self.pageSize = 10  # set changeable later
        self.countTotal = 'true'  # The parameter is ignored for the subsequent pages

        self.studies = []
        # write to CSV
        self.csvfilename = ''  #changeable
        self.csvfile = ''

        # change mode, choose between CSV and HTML
        self.filemode = filemode  # default mode
        self.htmlWriter = HTMLWriter()

        # handle pages
        self.pageTokens = ['', '']  # array of string pageToken. first 2 are dummies
        self.pageNumber = 1

        # Global params for studies
        self.resultTotal = 0
        self.docpos = 0
        self.docposFound = False
        self.studyIndices = []

    def setSecondaryAPI(self, API):
        if not isinstance(API, self.SecondaryAPI):
            raise TypeError('API must be an instance of SecondaryAPI Enum')
        else:
            self.secondaryAPI = str(API)

    def setStudyTitle(self, title):
        self.studyTitle = title

    def setCondition(self, condition):
        self.condition = condition

    def setTreat(self, treat):
        self.treat = treat

    def setTerm(self, term):
        self.term = term

    def setformat(self, format):
        '''
        :param format: default format is csv
        :return:
        '''
        self.format = format

    def getStudies(self, pageNum):
        studies = self.studies[self.pageSize * (pageNum - 1):self.pageSize * pageNum]
        print(f'******* pageNUM={pageNum} study length: {len(studies)} *******')
        print(f'Total study length: {len(self.studies)}')
        return studies

    def getIndices(self, pageNum):
        indices = self.studyIndices[self.pageSize * (pageNum - 1):self.pageSize * pageNum]
        return indices

    # functional setters
    def setPageSize(self, pageSize):
        self.pageSize = pageSize

    def setCountTotal(self, count):
        self.countTotal = count

    # search functions
    def addfield(self, field):
        '''
        Study Title and Study Document are by default
        # https://clinicaltrials.gov/data-api/about-api/csv-download
        :param field: field name to add to fields string
        :return: nothing
        '''
        self.fields += '|' + field

    def buildAggFilters(self, filter):
        if self.aggFilters == '':
            self.aggFilters = filter.strip()
        else:
            self.aggFilters = self.aggFilters + ',' + filter.strip()

    # TODO: add queries

    def buildurl(self):
        self.downloadurl = self.defaulturl + self.secondaryAPI

    # TODO: Search function.
    def search(self, pageNum=1):
        """
        when search button is pressed, all search params are already recorded in self
        :return: an array of studies and the indices noting which one is selected
        """
        self.buildurl()
        print('Searching...')
        # print(self.format)
        # print(self.condition)
        # print(self.term)
        # print(self.treat)
        # print(self.outcome)
        # print(self.studyTitle)
        # print(self.aggFilters)
        # print(self.fields)
        # print(f'pageSize={self.pageSize}')
        # print('Finished printing search params \n')
        # print('downloadurl: {}'.format(self.downloadurl))

        pageToken = self.getPageToken(pageNum)
        if pageNum > 1:
            fields = {
                "format": self.format,
                "query.titles": self.studyTitle,
                "query.cond": self.condition,
                "query.term": self.term,
                "query.intr": self.treat,
                "query.outc": self.outcome,
                "aggFilters": self.aggFilters,
                "fields": self.fields,
                "pageSize": self.pageSize,
                "countTotal": self.countTotal,
                "pageToken": pageToken
            }
        else:
            fields = {
                "format": self.format,
                "query.titles": self.studyTitle,
                "query.cond": self.condition,
                "query.term": self.term,
                "query.intr": self.treat,
                "query.outc": self.outcome,
                "aggFilters": self.aggFilters,
                "fields": self.fields,
                "pageSize": self.pageSize,
                "countTotal": self.countTotal
                # "pageToken": ''
            }

        # If study already exists, do not search

        start = self.pageSize * (pageNum - 1)
        end = self.pageSize * pageNum
        print(f'in search , before resp, pgeNum={pageNum} start={start} lenstudies={len(self.studies)}')
        if start < len(self.studies):
            print(f'already exists, returning...')
            return {
                'indices': self.studyIndices[start:end],
                'studies': self.studies[start:end]
            }
        print(f'Does not yet exist, appending studies')
        resp = urllib3.request(
            "GET",
            self.downloadurl,
            fields=fields
        )
        if pageNum == 1:
            self.resultTotal = int(resp.headers.get('x-total-count'))
            # print(f'resultTotaldebug: type={type(self.resultTotal)} value={self.resultTotal}')
        pageToken = resp.headers.get('x-next-page-token')
        # last page !
        if pageToken is None:
            # disable the next page button
            print('Empty page Token ,last one')
            print(type(pageToken))
            self.signals.disableNextBtn.emit(False)

        print('+++++++++++++++')
        print(f'pageNum={pageNum}')
        print(f'pageToken = {pageToken}')
        print(str(self.pageTokens))
        print('finished printing pageTokens')

        if pageToken is not None:
            self.pageTokens.append(pageToken)

        self.createStudies(resp=resp, pageNum=pageNum)  # append studies to self.studies[]

        studies = self.getStudies(pageNum)
        indices = self.getIndices(pageNum)

        return {
            'indices': indices,
            'studies': studies  # will be used to build table. should return studies for the current page.
        }

    @Slot()
    def download(self):
        '''
        stores studies into self. then download
        :param studyindex: array of int that points to studies in the studies[]
        :return:
        '''
        studies = []  # array of STUDY objects to download.
        # for index in self.indexToDownload:
        #     studies.append(self.studies[index])
        for i in range(0, len(self.studyIndices)):
            if self.studyIndices[i] == 1:
                studies.append(self.studies[i])

        if self.filemode == 'HTML':  # <- default choice
            self.writeToHTML(studies)
        elif self.filemode == 'CSV':
            self.writeToCSV(studies)
        else:
            print('ERROR: incorrect filemode')
            print(f"Current filemode is : {self.filemode} . You can only choose HTML or CSV")

        return

    def createStudies(self, resp=None, pageNum=1):
        """
        Create studies from http resp object
        :param resp:
        :return:
        """
        print('******* Creating Studies *******')
        data = resp.data.decode('utf-8')
        # print('resp.data:\n{}'.format(data))

        content = []
        reader = csv.reader(data.splitlines(), delimiter=',')
        for row in reader:
            content.append(row)
        print(f'content study numbers: {len(content)}')

        headers = content[0]
        # TODO: returned study documents seem to be always at the end ?
        if not self.docposFound:
            for i in range(0, len(headers)):
                # Study Documents position can be empty !
                if headers[i].strip() == 'Study Documents':
                    self.docpos = i
                    break

        # for each study, create a study object and store
        # 1st page has col names, others pages do not
        # TODO: dynamically get title
        start = 0 if self.docposFound else 1
        shift = 1 if self.docposFound else 0
        for i in range(start, len(content)):
            title = content[i][0]
            study = Study(
                title=title,
                docpos=self.docpos,
                index=i + shift + self.pageSize * (pageNum - 1),
                content=content[i]
            )
            self.studies.append(study)
            self.studyIndices.append(1)  # by default, all studies are selected

        self.docposFound = True

    def kill(self):
        self.is_killed = True
        self.htmlWriter.is_killed = True

    def addtocsv(self, csvString, filename, folder_path):
        """
        Assume that csv file goes into the same folder as download, change later
        :return:
        """
        # "=HYPERLINK(""http://www.Google.com"",""Google"")"
        header = csvString
        modifiedString = (header + '"=HYPERLINK(""' + folder_path + filename + '.pdf"",'
                          + '""' + filename + '"")",')
        return modifiedString

    def generateCSVLines(self, csvString):
        self.csvfile = self.csvfile + csvString + '\n'

    def writeToCSV(self, studies):
        # count progress bar by study numbers
        studylen = len(studies)

        for listindex, study in enumerate(studies):
            filenames = study.fileNames
            fileUrls = study.fileUrls
            # Parse study tile for valid folder name
            titletmp = re.sub(r'^\s|\\|/|:|\*|\?|"|<|>|\||\.', ' ', study.title).strip()
            # keep only 200 chars, change later
            validtitle = titletmp[0:100]
            validtitle = validtitle.strip()  # windows want no space or . in folder names
            # print('ValidTitle: {}'.format(validtitle))
            titlewindex = str(study.index) + '-' + validtitle
            # print('titlewindex: {}'.format(titlewindex))

            csvString = '"' + titletmp + '"' + ','  # First column in csv, Study Title
            # print('csvString: {}'.format(csvString))

            flen = len(filenames)
            try:
                for i in range(flen):
                    if self.is_killed:
                        raise WorkerKilledException
                    filename = filenames[i]
                    fileUrl = fileUrls[i]
                    print('fileurl: {}'.format(fileUrl))
                    resp = urllib3.request(
                        "GET",
                        fileUrl
                    )

                    directory = self.downloadFolder + titlewindex + '/'
                    # print('dir: {}'.format(directory))
                    file_path = os.path.join(directory, filename)
                    print('fp: {}'.format(file_path))

                    if not os.path.isdir(directory):
                        os.makedirs(directory)
                    with open(file_path + '.pdf', 'wb') as file:
                        file.write(resp.data)
                        file.close()

                    # TODO: figure out a good relative path
                    # relative path of csv file to download folder
                    relative_folder_path = './' + titlewindex + '/'
                    csvString = self.addtocsv(csvString, filename, relative_folder_path)

            except WorkerKilledException:
                print('Stop Button Pressed')
                pass
            self.generateCSVLines(csvString)
            # for Multi-Thread progress bar
            # TODO: calculate progress bar values.
            print(f'Emitting Value: {(listindex + 1) * 100 / studylen}')
            self.signals.updateProgressBar.emit((listindex + 1) * 100 / studylen)
        self.writeAlltoCSV()
        return

    def writeAlltoCSV(self):
        """
        Write results to a csv file with links
        # https://clinicaltrials.gov/data-api/about-api/csv-download
        :return:
        """
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %Hh%Mm%Ss")

        directory = self.downloadFolder
        file_path = os.path.join(directory, dt_string)
        with open(file_path + '.csv', 'wb') as file:
            file.write(self.csvfile.encode('utf-8'))
            file.close()

    def writeToHTML(self, studies):
        # get a new HTML folder and file for each download
        self.htmlWriter.update(
            studyTitle=self.studyTitle,
            condition=self.condition,
            treat=self.treat,
            term=self.term,
            studies=studies,
            signals=self.signals,
            downloadFolder=self.downloadFolder
        )
        # download first, then build HTML
        # download
        print(f'downloadfolder: {self.downloadFolder}')
        print('Starting htmlwriter')
        self.htmlWriter.writeToHTML()

        # build HTML from template
        return

    def getPageToken(self, pageNum):
        # soft check if it's last page

        if pageNum == 1:
            return ''
        else:
            return self.pageTokens[pageNum]

    def updateStudyIndices(self, studyIndices=None, pageNum=1):

        currentpage = pageNum
        arr = studyIndices

        start = self.pageSize * (currentpage - 1)
        end = start + len(studyIndices)

        # does current page exist ?
        exist = False
        if len(self.studies) > start:
            exist = True
        print('****** update study indices ******')
        print(f'start={start} end={end} pageNum={pageNum} exist={exist}')
        print('before update:')
        print(self.studyIndices)
        print('to update:')
        print(studyIndices)

        # if exist, update current page
        if exist:
            arritr = iter(arr)
            print('exists. updating')
            for i in range(start, end):
                self.studyIndices[i] = next(arritr)
        # else, append current page
        else:
            self.studyIndices.extend(studyIndices)

        print('after update:')
        print(self.studyIndices)
        print('finished updating study indices')
        return
