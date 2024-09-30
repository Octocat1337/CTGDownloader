import os
from datetime import datetime

import urllib3
from PySide6.QtCore import QRunnable, Slot, Signal
from urllib3 import Timeout

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p',
                    filename='CTD-log.log', encoding='utf-8', level=logging.INFO)
class WorkerKilledException(Exception):
    pass


class HTMLWriter(QRunnable):
    def __init__(self, **kwargs):
        super().__init__()
        self.parent = kwargs.get('parent', None)
        self.studyInfo = {
            'studyTitle': '',
            'conditon': '',
            'treat': '',
            'term': '',
            'studies': []
        }
        self.downloadFolder = ''
        self.HTMLFolderName = ''
        self.signals = None
        self.studies = None
        self.is_killed = False
        # Handle HTTP request timeout
        self.timeout = urllib3.util.Timeout(connect=3.0, read=3.0)
        self.retry = urllib3.util.Retry(connect=5, read=5, redirect=5)
        self.http = urllib3.PoolManager(timeout=self.timeout) # share the same timeouts

    def update(self, **kwargs):
        self.studyInfo.update(kwargs)
        self.HTMLFolderName = self.buildHTMLFolderName()
        self.signals = kwargs.get('signals')
        self.studies = kwargs.get('studies')
        self.downloadFolder = kwargs.get('downloadFolder')
        dlfldrpath = os.path.join(self.downloadFolder, self.HTMLFolderName)
        self.parent.parent.downloadFolderName = dlfldrpath

    def buildHTMLFolderName(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %Hh%Mm%Ss")
        queries = ' '.join(
            [self.studyInfo.get('studyTitle'),
             self.studyInfo.get('condition'),
             self.studyInfo.get('treat'),
             self.studyInfo.get('term')]
        ).strip()
        # limit the folder name length just in case
        queries_truncated = queries[:80]
        HTMLFolderName = 'CTD ' + queries_truncated + ' ' + dt_string
        return HTMLFolderName
    @Slot()
    def writeToHTML(self):

        # count progress bar by study numbers
        studylen = len(self.studies)

        # read in HTML template
        templateFileName = 'indexTemplate.html'
        templateFolder = 'resources'

        templatePath = os.path.join(templateFolder, templateFileName)
        htmlfile = open(templatePath, 'r', encoding='utf-8')
        htmlcontent = htmlfile.readlines()
        htmlfile.close()
        logger.info('HTMLWriter: loaded template')
        endline = 0
        for linenumber, line in enumerate(htmlcontent):
            if line.find('table ends') > 0:
                endline = linenumber
                break

        # file names: default filenames.
        # example: ProtocolAndSAP
        for listindex, study in enumerate(self.studies):
            if self.is_killed:
                break
            logger.info(f'---------- New Study {study.index}----------')
            # one name : one url
            filenames = study.fileNames
            fileUrls = study.fileUrls

            # Write HTML: HTML file exists under download/
            # files exists in download/foldername/studyindex
            # table row header
            line = '<tr>\n'
            htmlcontent.insert(endline, line)
            endline += 1
            # index
            line = f'<td>{study.index}</td>\n'
            htmlcontent.insert(endline, line)
            endline += 1
            # folder
            study_dir = os.path.join(str(study.index))
            line = f'<td><a href="{study_dir}" target=_blank>{study.title}</a></td>\n'
            htmlcontent.insert(endline, line)
            endline += 1

            # download study files
            flen = len(filenames)

            try:
                for i in range(flen):
                    if self.is_killed:
                        #TODO: reset progrss bar
                        raise WorkerKilledException
                    oldfilename = filenames[i]
                    filename = str(study.index) + '-' + filenames[i]
                    fileUrl = fileUrls[i]
                    # get suffix, in case it's not a pdf file.
                    suffix = fileUrl.split('.')[-1]

                    logger.info('New File')
                    logger.info('fileurl: {}'.format(fileUrl))
                    try:
                        resp = self.http.request(
                            "GET",
                            fileUrl,
                            timeout=Timeout(5)
                        )
                    # TODO: update the table to display status
                    except urllib3.exceptions.ConnectTimeoutError:
                        logger.info('Connect Timeout')
                        continue
                    except urllib3.exceptions.ReadTimeoutError:
                        logger.info('Read Timeout')
                        continue
                    except urllib3.exceptions.MaxRetryError:
                        logger.info('Max Retry 7 times reached')
                        continue

                    directory = os.path.join(self.downloadFolder, self.HTMLFolderName, str(study.index))
                    file_path = os.path.join(directory, filename)

                    if not os.path.isdir(directory):
                        os.makedirs(directory)

                    file_path2 = file_path + '.' + suffix
                    logger.info(f'fp: {file_path2}')

                    with open(file_path2, 'wb') as file:
                        file.write(resp.data)
                    logger.info('Finished writing file to folder')

                    #TODO: check line2. should I use path.join ?
                    file_path3 = os.path.join(str(study.index), filename+'.'+suffix)
                    # line2 = (f'<td><a href="{self.HTMLFolderName}/{str(study.index)}/{filename}.{suffix}" target=_blank>'
                    #     f'{oldfilename}</a></td>\n'
                    # )
                    line2 = (f'<td><a href="{file_path3}" target=_blank>'
                        f'{oldfilename}</a></td>\n'
                    )
                    logger.info(f'htmlline: {line2}')
                    htmlcontent.insert(endline, line2)
                    endline += 1

            except WorkerKilledException:
                logger.info('Stop Button Pressed')
                pass

            line = '</tr>\n'
            htmlcontent.insert(endline, line)
            endline += 1
            # for Multi-Thread progress bar
            # TODO: calculate progress bar values.
            logger.info(f'Emitting Value: {(listindex + 1) * 100 / studylen}')
            if not self.is_killed:
                self.signals.updateProgressBar.emit((listindex + 1) * 90 / studylen)
            else:
                self.signals.updateProgressBar.emit(0)

        if self.is_killed:
            self.signals.updateProgressBar.emit(0)
        # Write to real HTML File
        # indexFilePath = os.path.join(self.downloadFolder, self.HTMLFolderName+' index.html')
        indexFilePath = os.path.join(self.downloadFolder, self.HTMLFolderName, 'index.html')

        # process encodes
        htmlcontent2 = []
        for content in htmlcontent:
            htmlcontent2.append(content.encode('utf-8'))

        with open(indexFilePath, 'wb+') as file:
            for content in htmlcontent2:
                file.write(content)


        # all done. Enable download button and do a popup
        if not self.is_killed:
            self.signals.updateProgressBar.emit(100)
            self.signals.updateDownloadButton.emit(True)


