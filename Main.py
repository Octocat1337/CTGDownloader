import requests
import urllib3
import io
import pandas as pd
import re

server = 'https://clinicaltrials.gov/api/v2'

studies = '/studies'

# query = '?query.titles=Prognostic Value of the 6-minute Stepper Test in Non-small Cell Lung Cancer Surgery'
# query2 = '/NCT02394548?format=csv&fields=Study Documents'
# query2 = '/NCT02394548'
# query = '?query.titles=Prognostic Value of the 6-minute Stepper Test in Non-small Cell Lung Cancer Surgery'


# url = server + studies + query2
url = server + studies
# resp = urllib3.request("GET", url)
resp = urllib3.request(
    "GET",
    url,
    fields={
        "format": "csv",
        "query.titles": "small Cell Lung Cancer",
        "fields": "Study Title" + '|' + "Study Documents"
    }

)
# resp.auto_close = False

print(resp.status)
print(resp.headers)
print(resp.data)
# content = data.decode('utf-8')
# content2 = re.search(b".*\"(.*)\"",data).group(1)
# content3 = content2.decode("utf-8")
# content4 = re.sub(r"\|",",",content3)
# print(content3)
# print(content4)
#
#
# # based on how may papers are found, get each csv
#
# # df = pd.DataFrame(data)
# # df.to_csv('test2.csv')
#
# with open('test.csv',"wb") as fp:
#         fp.write(content4.encode("utf-8"))
#         fp.close()

# open the file and download links inside

#####
# "https://clinicaltrials.gov/api/v2/studies?query.titles=CARdioprotection+in+Myocardial+Infarction" \
#  -H "accept: application/json"
