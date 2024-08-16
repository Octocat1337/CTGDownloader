from PySide6.QtWidgets import QApplication
import sys
from UI import CTDWindow
import re

if __name__ == '__main__':
    app = QApplication()
    window = CTDWindow()
    window.show()
    sys.exit(app.exec())
    # tmp2: after file separation
    # tmp2 = '"Study Protocol, Statistical Analysis Plan, and Informed Consent Form, https://cdn.clinicaltrials.gov/large-docs/74/NCT00421174/Prot_SAP_ICF_000.pdf"'
    # tmp3 = tmp2.split(',')
    #
    # pattern = re.compile(r'\s+|"')
    # filename = re.sub(pattern, '', tmp3[0])
    # fileurl = re.sub(pattern, '', tmp3[1])
    #
    # # filename2 = re.sub(r'','',tmp)tm
    #
    # # step1, remove " and white space
    # tmp3 = re.sub(r'\s+|"','',tmp2)
    # filename2 = re.sub(r'(.*)http.*',r'\1',tmp3)
    # fileurl2 = re.sub(r'.*(http.*\..*)',r'\1',tmp3)
    #
    #
    #
    # print('tmp3={}'.format(tmp3))
    # print('filename2={}'.format(filename2))
    # print('fileurl2={}'.format(fileurl2))
    # print('filename: []'.format(filename))
    # print('fileurl: {}'.format(fileurl))
