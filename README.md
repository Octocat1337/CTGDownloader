Clinical Trial gov file downloader
downloads files from clinicaltrials.gov

What to do :
  run the CTD.py file

requirements:
python 11
pyside6
urllib3


Current featrues:
  Search by study title, documents(protocol/SAP/ICF)
  Search by study Phase etc

The default is 10 articles. 
next page/prev page feature is not implemented.

If you want to show more results, change the setPageSize function argument in UI.py

Application will create a 'download' folder in your current folder and a csv file with clickable filenames
