import urllib3

from Downloader import Downloader
from urllib3 import request

# simulate a press of the download button
if __name__ == '__main__':
    d = Downloader()
    # d.setStudyTitle('Safety of Pentoxifylline and Vitamin E With Stereotactic Ablative Radiotherapy (SABR) in Non-small Cell Lung Cancers')
    d.setCondition('Small Cell Lung Cancer')
    d.setPageSize(2)
    d.setaggFilter('docs:prot')
    d.setCountTotal('true')
    # d.setformat('json')

    # Button pressed
    d.download()


    # question: same search condition gives diff results on website
    # https://clinicaltrials.gov/search?cond=Non-small%20Cell%20Lung%20Cancer

    # website search yields different results from CSV/JSON search. However, the result is the same but in diff orders.
    # csv returns brief title, which is not found on website
    # json returns full official title, but is too long.
