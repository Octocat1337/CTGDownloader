import os
import re
from datetime import datetime

import urllib3
from PySide6.QtCore import QRunnable, Slot, Signal


class WorkerKilledException(Exception):
    pass


class HTMLWriter(QRunnable):
    def __init__(self, **kwargs):
        super().__init__()
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

    def update(self, **kwargs):
        self.studyInfo.update(kwargs)
        self.HTMLFolderName = self.buildHTMLFolderName()
        self.signals = kwargs.get('signals')
        self.studies = kwargs.get('studies')
        self.downloadFolder = kwargs.get('downloadFolder')

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
        htmlfile = open('indexTemplate.html', 'r')
        htmlcontent = htmlfile.readlines()
        htmlfile.close()

        endline = 0
        for linenumber, line in enumerate(htmlcontent):
            if line.find('table ends') > 0:
                endline = linenumber
                break


        # file names: default filenames.
        # example: ProtocolAndSAP
        for listindex, study in enumerate(self.studies):
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
            # line = f'<td><a href="{self.HTMLFolderName}/{str(study.index)}" target=_blank>{self.HTMLFolderName}</a></td>\n'
            # htmlcontent.insert(endline, line)
            # endline += 1
            # study name
            line = f'<td><a href="{self.HTMLFolderName}/{str(study.index)}" target=_blank>{study.title}</a></td>\n'
            htmlcontent.insert(endline, line)
            endline += 1

            # download study files
            flen = len(filenames)
            try:
                for i in range(flen):
                    if self.is_killed:
                        raise WorkerKilledException
                    oldfilename = filenames[i]
                    filename = str(study.index) + '-' + filenames[i]
                    fileUrl = fileUrls[i]
                    # get suffix, in case it's not a pdf file.
                    suffix = fileUrl.split('.')[-1]

                    print('New Study')
                    print('fileurl: {}'.format(fileUrl))
                    resp = urllib3.request(
                        "GET",
                        fileUrl
                    )
                    # print('finished getting resp')
                    # print(filename)
                    # print(self.downloadFolder) # NONE ????
                    # print(self.HTMLFolderName)

                    directory = self.downloadFolder + '/' + self.HTMLFolderName + '/' + str(study.index)
                    # print('dir: {}'.format(directory))
                    file_path = os.path.join(directory, filename)
                    print('fp: {}'.format(file_path))

                    if not os.path.isdir(directory):
                        os.makedirs(directory)

                    print(suffix)
                    file_path2 = file_path + '.' + suffix
                    print(file_path2)
                    with open(file_path2, 'wb') as file:
                        file.write(resp.data)

                    print('Finished writing')
                    line2 = (f'<td><a href="{self.HTMLFolderName}/{str(study.index)}/{filename}.{suffix}" target=_blank>'
                        f'{oldfilename}</a></td>\n'
                    )
                    htmlcontent.insert(endline, line2)
                    endline += 1

            except WorkerKilledException:
                print('Stop Button Pressed')
                pass
            line = '</tr>\n'
            htmlcontent.insert(endline, line)
            endline += 1
            # for Multi-Thread progress bar
            # TODO: calculate progress bar values.
            print(f'Emitting Value: {(listindex + 1) * 100 / studylen}')
            self.signals.updateProgressBar.emit((listindex + 1) * 90 / studylen)

        # Write to real HTML File
        with open(self.downloadFolder + '/' + self.HTMLFolderName + ' index.html', 'w') as file:
            file.writelines(htmlcontent)

        # all done. Enable download button and do a popup
        self.signals.updateProgressBar.emit(100)
        self.signals.updateDownloadButton.emit(True)


