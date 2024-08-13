from enum import Enum

import urllib3
from urllib3 import request


class Downloader:
    class SecondaryAPI(Enum):
        studies = '/studies'
        nctID = '/studies/'
        metadata = '/studies/metadata'

        def __str__(self):
            ...
            return str(self.value)

    def __init__(self):

        self.defaulturl = 'https://clinicaltrials.gov/api/v2'
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

    def setSecondaryAPI(self, API):
        if not isinstance(API, self.SecondaryAPI):
            raise TypeError('API must be an instance of SecondaryAPI Enum')
        else:
            self.studies = str(API)

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
    def setaggFilter(self,filter):
        if self.aggFilters == '':
            self.aggFilters = filter
        else:
            self.aggFilters = self.aggFilters + '|' + filter
    # TODO: add queries
    def buildurl(self):
        self.downloadurl = self.defaulturl + self.secondaryAPI

    def download(self):
        resp = urllib3.request(
            "GET",
            self.downloadurl,
            fields={
                "format": self.format,
                "query.titles": self.studyTitle,
                "query.cond": self.condition,
                "aggFilters":self.aggFilters,
                "fields": self.fields,
                "pageSize": self.pageSize,
                "countTotal": self.countTotal
            }
        )
        return resp

# https://clinicaltrials.gov/data-api/about-api/csv-download
