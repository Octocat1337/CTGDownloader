import json
import re
class Study:
    def __init__(self, *args):
        """
        init study
        :param args: title,docpos,index,[(fileName,fileUrl)]
        """
        # innate property
        self.title = ''
        self.index = -1
        # params for args
        self.titlepos = 0
        self.docpos = 1
        self.indexpos = 2
        self.filespos = 3
        #
        self.hasProtocol = False
        self.hasSAP = False
        self.hasICF = False
        # URL
        self.ProtocolUrl = ''
        self.SAPUrl = ''
        self.ICFUrl = ''
        # Name
        self.ProtocolName = 'Protocol_'
        self.SAPName = 'SAP_'
        self.ICFName = 'ICF_'

        # method 2. keep documents as is
        # args is passed as an array of tuple
        # title, docpos,index,[separated study lines]
        self.fileNames = []
        self.fileUrls = []

        self.args = args
        self.parseArgs2()
    def parseArgs2(self):
        """
        Parse args for method 2
        :return:
        """
        # setup properties
        self.title = self.args[self.titlepos].strip()
        self.index = self.args[self.indexpos]
        docpos = self.args[self.docpos]

        # setup study documents
        docs = self.args[self.filespos][docpos]
        docscontent = []
        if docs == '':
            return

        tmp = docs.split('|')
        for tmp2 in tmp:
            tmp3 = re.sub(r'\s+|"', '', tmp2)
            filename = re.sub(r'(.*),\s*http.*', r'\1', tmp3)
            fileurl = re.sub(r'.*(http.*\..*)', r'\1', tmp3)

            docscontent.append((filename, fileurl))

        # self.docNames =
        for tuple in docscontent:
            filename,fileurl = tuple
            self.fileNames.append(filename)
            self.fileUrls.append(fileurl)

    def setProtocolStatus(self, status):
        self.hasProtocol = status

    def setSAPStatus(self, status):
        self.hasSAP = status

    def setICFStatus(self, status):
        self.hasICF = status

    # set urls
    def setProtocolUrl(self, url):
        self.ProtocolUrl = url

    def setSAPUrl(self, url):
        self.SAPUrl = url

    def setICFUrl(self, url):
        self.ICFUrl = url

    # set file name / study document name ?
    def setProtocolName(self, name):
        self.ProtocolName = name

    def setSAPName(self, name):
        self.SAPName = name

    def setICFName(self, name):
        self.ICFName = name
