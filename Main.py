# import requests
import urllib3
# import io
# import pandas as pd
# import re
#
# server = 'https://clinicaltrials.gov/api/v2'
#
# studies = '/studies'
#
# # query = '?query.titles=Prognostic Value of the 6-minute Stepper Test in Non-small Cell Lung Cancer Surgery'
# # query2 = '/NCT02394548?format=csv&fields=Study Documents'
# # query2 = '/NCT02394548'
# # query = '?query.titles=Prognostic Value of the 6-minute Stepper Test in Non-small Cell Lung Cancer Surgery'
#
#
# # url = server + studies + query2
# url = server + studies
# # resp = urllib3.request("GET", url)
# resp = urllib3.request(
#     "GET",
#     url,
#     fields={
#         "format": "csv",
#         "query.titles": "small Cell Lung Cancer",
#         "fields": "Study Title" + '|' + "Study Documents"
#     }
#
# )
# resp.auto_close = False

# print(resp.status)
# print(resp.headers)
# # get each line and data
# data = resp.data
# print(data)
# content = data.decode('utf-8')
# print(content)

# Test data :
content = """Study Title,Study Documents
Imatinib Mesylate After Irinotecan and Cisplatin in Treating Patients With Extensive-Stage Small Cell Lung Cancer,
Phase III Open Label First Line Therapy Study of MEDI 4736 (Durvalumab) With or Without Tremelimumab Versus SOC in Non Small-Cell Lung Cancer (NSCLC),"Study Protocol, https://cdn.clinicaltrials.gov/large-docs/82/NCT02453282/Prot_014.pdf|Statistical Analysis Plan, https://cdn.clinicaltrials.gov/large-docs/82/NCT02453282/SAP_000.pdf"
Efficacy of Cadonilimab in Non-squamous Non-small Cell Lung Cancer Patients Resistant to EGFR-TKI,
"""

contentarray = content.splitlines()
print(contentarray[0])
studies = []
print(contentarray[2])

study = contentarray[2].split(',',1)
for string in study:
    print(string)

title = study[0].strip(',').strip()
documents = study[1].strip('\"').split('|')
protocolurl = documents[0].split(',')[1].strip()
print(protocolurl)
resp = urllib3.request(
    "GET",
    protocolurl
)
with open(title+'.pdf','wb') as file:
    file.write(resp.data)
    file.close()







# for i in range(1,len(contentarray)):
#     study = contentarray[i].split(',')
#     documents = study[1].strip('\"')
#     studies.append({
#         'title': study[0].strip(','),
#         'sap': documents[0],
#         'icf': documents[1]
#     })
#
# print(len(studies))





# get next page token

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
