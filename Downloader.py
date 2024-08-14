from enum import Enum
import os.path
import urllib3
from urllib3 import request
from Study import Study
import re
from datetime import datetime

class Downloader:
    class SecondaryAPI(Enum):
        studies = '/studies'
        nctID = '/studies/'
        metadata = '/studies/metadata'

        def __str__(self):
            return str(self.value)

    def __init__(self):

        self.defaulturl = 'https://clinicaltrials.gov/api/v2'
        self.downloadFolder = './'
        self.secondaryAPI = str(self.SecondaryAPI.studies)
        self.downloadurl = ''
        self.fields = 'Study Title|Study Documents'
        self.format = 'csv'
        # optional search args
        self.studyTitle = ''
        self.condition = ''
        self.aggFilters = ''

        # functional args
        self.pageSize = 10
        self.countTotal = 'false'

        self.studies = []
        self.csvfilename = ''  #changeable
        self.csvfile = ''

    def setSecondaryAPI(self, API):
        if not isinstance(API, self.SecondaryAPI):
            raise TypeError('API must be an instance of SecondaryAPI Enum')
        else:
            self.secondaryAPI = str(API)

    def setStudyTitle(self, title):
        self.studyTitle = title

    def setCondition(self, condition):
        self.condition = condition

    def setformat(self, format):
        '''
        :param format: default format is csv
        :return:
        '''
        self.format = format

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

    def setaggFilter(self, filter):
        if self.aggFilters == '':
            self.aggFilters = filter
        else:
            self.aggFilters = self.aggFilters + '|' + filter

    # TODO: add queries
    def buildurl(self):
        self.downloadurl = self.defaulturl + self.secondaryAPI

    # when download button is pressed, run this function
    def download(self):
        self.buildurl()
        resp = urllib3.request(
            "GET",
            self.downloadurl,
            fields={
                "format": self.format,
                "query.titles": self.studyTitle,
                "query.cond": self.condition,
                "aggFilters": self.aggFilters,
                "fields": self.fields,
                "pageSize": self.pageSize,
                "countTotal": self.countTotal
            }
        )
        self.createStudies(resp)
        self.savefiles()

    def createStudies(self, resp):
        """
        Create studies from http resp object
        :param resp:
        :return:
        """
        data = resp.data.decode('utf-8')
        # print(type(data))  string
        lines = data.splitlines()
        # TODO: Dynamically get study documents
        allcols = lines[0]  # Study Title, Study Documents etc.
        docpos = -1
        colnames = allcols.split(',')

        # find doc position
        for i in range(0, len(colnames)):
            if colnames[i].strip() == 'Study Documents':
                docpos = i
                break
            else:
                continue

        # for each study, create a study object and store
        for i in range(1, len(lines)):
            tmp = lines[i].split(',\"')
            # tmp = lines[1].split(',\"')
            title = tmp[0]
            study = Study(title, docpos, tmp)
            self.studies.append(study)

        print(resp.headers.get('x-total-count'))

    def savefiles(self):
        '''
        takes http reponse and get its data
        for each study in studies[]
        download the file and save it
        :return: nothing
        '''
        for study in self.studies:
            filenames = study.fileNames
            fileUrls = study.fileUrls
            # Parse study tile for valid folder name
            validtitle = re.sub(r'\\|/|:|\*|\?|"|<|>|\|', ' ', study.title)
            print(validtitle)
            csvString = '"' + validtitle + '"'+','
            for i in range(len(filenames)):
                filename = filenames[i]
                fileUrl = fileUrls[i]

                print(filename)
                print(fileUrl)
                resp = urllib3.request(
                    "GET",
                    fileUrl
                )


                directory = self.downloadFolder + validtitle + '/'
                file_path = os.path.join(directory, filename)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                with open(file_path + '.pdf', 'wb') as file:
                    file.write(resp.data)
                    file.close()

                csvString = self.addtocsv(csvString, filename, file_path)

            self.writeLinetoCSV(csvString)
        self.writeAlltoCSV()
        # if study.hasProtocol:
        #     resp = urllib3.request(
        #         "GET",
        #         study.ProtocolUrl
        #     )
        #     directory = './' + self.downloadFolder + '/'
        #     filename = study.ProtocolName
        #     file_path = os.path.join(directory, filename)
        #     if not os.path.isdir(directory):
        #         os.makedirs(directory)
        #     with open(file_path + '.pdf', 'wb') as file:
        #         file.write(resp.data)
        #         file.close()

    def addtocsv(self,csvString,filename,file_path):
        """
        Assume that csv file goes into the same folder as download, change later
        :return:
        """
        # "=HYPERLINK(""http://www.Google.com"",""Google"")"
        header = csvString
        modifiedString = (header + '"=HYPERLINK(""' + file_path + '.pdf"",'
                          + '""' + filename + '"")",')
        return modifiedString
    def writeLinetoCSV(self,csvString):
        self.csvfile = self.csvfile + csvString + '\n'

    def writeAlltoCSV(self):

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %HH%MM%Ss")

        directory = self.downloadFolder
        file_path = os.path.join(directory, dt_string)
        with open(file_path + '.csv', 'wb') as file:
            file.write(self.csvfile.encode('utf-8'))
            file.close()

# https://clinicaltrials.gov/data-api/about-api/csv-download
