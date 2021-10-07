import csv
import requests
import json
import urllib.request
import glob
import os
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

#### CONFIG ####
searchQuery = 'mensenhandel'
baseUrl = 'https://uitspraken.rechtspraak.nl/api/zoek'
LiDoBaseUrl = 'https://linkeddata.overheid.nl/front/portal/document-viewer?ext-id='
uitsprakenBaseUrl = 'https://uitspraken.rechtspraak.nl/inziendocument?id='
case_count = 4000
save_text_location = os.getcwd() + '/data/'
################

cases_df = pd.DataFrame()
    
def getCaseText(caseId):
    response = requests.get(uitsprakenBaseUrl + caseId)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_content = soup.find("div", {"id": 'content'})
    uitspraak_html = soup_content.find('div', {'class': 'uitspraak'})
    if soup_content.find('div', {'class': 'uitspraak'}) is not None:
        uitspraak_html = soup_content.find('div', {'class': 'uitspraak'})
    elif soup_content.find('div', {'class': 'conclusie'}) is not None:
        uitspraak_html =  soup_content.find('div', {'class': 'conclusie'})
    uitspraak = uitspraak_html.get_text().replace("\n", '')
    uitspraak = uitspraak.replace(',', '')
    return uitspraak


def parseCaseInfo(results):
    global cases_df
    for case in results:
        caseText = getCaseText(case['TitelEmphasis'])
        # print(caseText[0:100])
        #case['Uitspraak'] = caseText
        parsedId = case['TitelEmphasis'].replace(':', '-')
        f= open(save_text_location + parsedId + ".txt","w+", encoding='utf-8')
        f.write(caseText)
        case['Case ID'] = parsedId
        cases_df = cases_df.append(case, ignore_index = True)
        print('Processed case', case['Case ID'])
    cases_df.to_csv('cases.csv', index=False)

def queryUitspraak():
    print("Querying")
    files = {"StartRow":0,"PageSize":case_count,"ShouldReturnHighlights":'true',"ShouldCountFacets":'true',"SortOrder":"Relevance","SearchTerms":[{"Term":searchQuery,"Field":"AlleVelden"}],"Contentsoorten":[],"Rechtsgebieden":[],"Instanties":[],"DatumPublicatie":[],"DatumUitspraak":[],"Advanced":{"PublicatieStatus":"AlleenGepubliceerd"},"CorrelationId":"9abc658b0ce64f8786992af6965aabc4","Proceduresoorten":[]}
    try:
        response = requests.post(baseUrl, json=files)
        responseJSON = json.loads(response.text)
        results = responseJSON['Results']
        print(len(results), "records!")
        parseCaseInfo(results)
    except urllib.error.HTTPError as err:
        print(err)

queryUitspraak()
