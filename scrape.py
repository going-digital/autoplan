import requests
from requests.exceptions import RequestException
#import logging
from contextlib import closing
from bs4 import BeautifulSoup
import urllib.parse

import http.client as http_client
#http_client.HTTPConnection.debuglevel = 1
#logging.basicConfig()
#logging.getLogger().setLevel(logging.ERROR)
#requests_log = logging.getLogger('requests.packages.urllib3')
#requests_log.setLevel(logging.ERROR)
#requests_log.propogate = True

# TODO: Get planning application numbers within search criteria
# TODO: Get document details for each planning application
# TODO: Download each document above

# https://opencagedata.com/api Free reverse geocoding

class Planning():
    def __init__(self, params):
        print('Opening session')
        self.s = requests.Session()
        data = {
            'searchCriteria.reference': '',
            'searchCriteria.planningPortalReference': '',
            'searchCriteria.alternativeReference': '',
            'searchCriteria.description': '',
            'searchCriteria.applicantName': '',
            'searchCriteria.caseType': '',
            'searchCriteria.ward': '',
            'searchCriteria.parish': 'LWTOFT',
            'searchCriteria.conservationArea': '',
            'searchCriteria.agent': '',
            'searchCriteria.caseStatus': '',
            'searchCriteria.caseDecision': '',
            'searchCriteria.appealStatus': '',
            'searchCriteria.appealDecision': '',
            'searchCriteria.developmentType': '',
            'caseAddressType': 'Application',
            'searchCriteria.address': '',
            'date(applicationReceivedStart)': '',
            'date(applicationReceivedEnd)': '',
            'date(applicationValidatedStart)': '',
            'date(applicationValidatedEnd)': '',
            'date(applicationCommitteeStart)': '',
            'date(applicationCommitteeEnd)': '',
            'date(applicationDecisionStart)': '',
            'date(applicationDecisionEnd)': '',
            'date(appealDecisionStart)': '',
            'date(appealDecisionEnd)': '',
            'searchType': 'Application'
        }

        for k,v in params.items():
            data[k] = v

        def parse_response(response):
            soup = BeautifulSoup(response, 'html.parser')
            results = soup.html.body.find('ul', {'id': 'searchresults'}).find_all('li')
            #print(results)
            processed = []
            for result in results:
                address = result.find('p', {'class': 'address'}).contents[0].strip()
                reference = result.find('p', {'class': 'metaInfo'}).contents[0].split('\n')[2].strip()
                processed.append({
                    'title': result.a.string.strip(),
                    'address': address,
                    'doc_url': "https://publicaccess.eastsuffolk.gov.uk" + result.a['href'],
                    'google_maps': "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(address),
                    'reference': reference
                })
            return processed


        # Connect to Planning portal, get references
        print('Searching')
        p = {}
        url = 'https://publicaccess.eastsuffolk.gov.uk/online-applications/advancedSearchResults.do?action=firstPage'
        r = self.s.post(url, data=data, stream=True)
        processed = parse_response(r.content)
        if len(processed) >= 20:
            # Only got first 20 results. Need to refetch with 100 results per page.
            print('Got full page. Refetching with 100 results per page.')
            r2 = self.s.post(
                'https://publicaccess.eastsuffolk.gov.uk/online-applications/pagedSearchResults.do',
                data={
                    'searchCriteria.page': 1,
                    'action': 'page',
                    'orderBy': 'DateReceived',
                    'orderByDirection': 'Descending',
                    'searchCriteria.resultsPerPage': '100'
                }
            )
            processed = parse_response(r2)

        self.processed = processed
    
    def read(self):
        return self.processed


    def ext_documents(self, id):
        url = "http://publicaccessdocuments.eastsuffolk.gov.uk/AniteIM.WebSearch/ExternalEntryPoint.aspx"
        params = {
            "SEARCH_TYPE": 1,
            "DOC_CLASS_CODE": "DC",
            "FOLDER1_REF": id
        }
        r = self.s.get(url, params=params, stream=True)
        #print(r.content)
        soup = BeautifulSoup(r.content, 'html.parser')
        # TODO: This defaults to 25 records per page. Number of records is on page
        print(soup.html.body)
        print(soup.html.body.find('div', {'class': 'TitleLabel'}))
        num_documents = int(
            soup
            .html
            .body
            .find('div', {'class': 'TitleLabel'})
            .contents[0]
            .split('-')[1]
            .split()[0]
        )
        documents = soup.html.body.find('table', {'id':'grdResults_tblData'}).find_all('tr')
        return num_documents, documents
"""
<a href="

http://publicaccessdocuments.eastsuffolk.gov.uk/AniteIM.WebSearch/ExternalEntryPoint.aspx?
SEARCH_TYPE=1
&DOC_CLASS_CODE=DC
&FOLDER1_REF=DC/19/1890/TPO


" target="_blank" title="View associated documents (opens in a new window)">
                View associated documents
            <span class="hide">(Opens in a new window)</span></a>
    """


p = Planning({
    'searchCriteria.parish': 'LWTOFT',
    'searchCriteria.ValidatedStart': '01/05/2019',
    'searchCriteria.ValidatedEnd': '12/05/2019'
})        

#print(p.read())
print(p.ext_documents('DC/19/1797/FUL'))