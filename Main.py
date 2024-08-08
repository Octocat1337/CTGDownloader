import requests
import urllib3

server = 'https://clinicaltrials.gov/api/v2'

studies = '/studies'

query = '?query.titles=Prognostic Value of the 6-minute Stepper Test in Non-small Cell Lung Cancer Surgery'
query2 = '/NCT02394548?format=csv&fields=Study Documents'

url = server + studies + query2

resp = urllib3.request("GET", url)

print(resp.status)
print(resp.headers)
print(resp.data)
#####
# "https://clinicaltrials.gov/api/v2/studies?query.titles=CARdioprotection+in+Myocardial+Infarction" \
#  -H "accept: application/json"