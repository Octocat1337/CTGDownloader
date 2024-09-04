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
    downloadButton = Signal(bool)

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
        self.countTotal = 'true'  # always get count number

        self.studies = []
        # write to CSV
        self.csvfilename = ''  #changeable
        self.csvfile = ''

        # change mode, choose between CSV and HTML
        self.filemode = filemode  # default mode
        self.htmlWriter = HTMLWriter()

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

    def getStudies(self):
        return self.studies

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
    def search(self):
        '''
        when search button is pressed
        :return: an array of studies, self.studies[]
        '''
        self.buildurl()
        print('Searching...')
        print(self.format)
        print(self.condition)
        print(self.term)
        print(self.treat)
        print(self.outcome)
        print(self.studyTitle)
        print(self.aggFilters)
        print(self.fields)
        print(f'pageSize={self.pageSize}')
        print('Finished printing search params \n')
        # print('downloadurl: {}'.format(self.downloadurl))
        resp = urllib3.request(
            "GET",
            self.downloadurl,
            fields={
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
            }
        )
        count = resp.headers.get('x-total-count')
        # print(count)
        # print()
        # print(resp.data)
        self.createStudies(resp)
        return {
            'count': count,
            'studies': self.studies
        }

    @Slot()
    def download(self):
        '''
        stores studies into self. then download
        :param studyindex: array of int that points to studies in the studies[]
        :return:
        '''
        studies = []  # array of STUDY objects to download.
        for index in self.indexToDownload:
            studies.append(self.studies[index])

        if self.filemode == 'HTML':  # <- default choice
            self.writeToHTML(studies)
        elif self.filemode == 'CSV':
            self.writeToCSV(studies)
        else:
            print('ERROR: incorrect filemode')
            print(f"Current filemode is : {self.filemode} . You can only choose HTML or CSV")

        return

    def createStudies(self, resp):
        """
        Create studies from http resp object
        :param resp:
        :return:
        """
        data = resp.data.decode('utf-8')
        print('resp.data:\n{}'.format(data))

        content = []
        reader = csv.reader(data.splitlines(), delimiter=',')
        for row in reader:
            content.append(row)

        docpos = -1
        headers = content[0]
        # TODO: returned study documents seem to be always at the end ?
        for i in range(0, len(headers)):
            # Study Documents position can be empty !
            if headers[i].strip() == 'Study Documents':
                docpos = i
                break
            else:
                continue

        # for each study, create a study object and store
        for i in range(1, len(content)):
            title = content[i][0]
            study = Study(title, docpos, i, content[i])
            self.studies.append(study)

        # # TODO: Dynamically get study documents
        # allcols = lines[0]  # Study Title, Study Documents etc.
        # docpos = -1
        # colnames = allcols.split(',')
        #
        # # find doc position,
        # # TODO: find other columns later
        # for i in range(0, len(colnames)):
        #     # Study Documents position can be empty !
        #     if colnames[i].strip() == 'Study Documents':
        #         docpos = i
        #         break
        #     else:
        #         continue
        #
        # # for each study, create a study object and store
        # for i in range(1, len(lines)):
        #     tmp = lines[i].split(',\"')
        #     print('tmp:  ' + str(tmp))
        #     title = tmp[0]
        #     study = Study(title, docpos, i, tmp)
        #     self.studies.append(study)

        # tmp = lines[1].split(',\"')
        # title = tmp[0]
        # study = Study(title, docpos, tmp)
        # self.studies.append(study)

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
