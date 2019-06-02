import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib.parse
import enum
import datetime
from pprint import pprint
import os

BASE_URL = "https://publicaccess.eastsuffolk.gov.uk"
BASE_URL_DOC =  "http://publicaccessdocuments.eastsuffolk.gov.uk/AniteIM.WebSearch/"

class Planning():
    def __init__(self):
         self.s = requests.Session()       

    def get_application(self, reference):
        # Fetch application metadata based on an application number
        query = {
            'searchType': 'Application',
            'searchTypeStatus': 'All',
            'searchCriteria.simpleSearchString': reference,
            'searchCriteria.simpleSearch': 'true'
        }        
        url = BASE_URL + '/online-applications/simpleSearchResults.do?action=firstPage'
        r1 = self.s.post(url, data=query, stream=True)
        soup = BeautifulSoup(r1.content, 'html.parser')
        results = {}
        url = BASE_URL + soup.find(id='tab_summary')['href']
        url_public_comments = BASE_URL + soup.find(id='tab_makeComment')['href']
        url_constraints = BASE_URL + soup.find(id='tab_constraints')['href']
        url_related = BASE_URL + soup.find(id='tab_relatedCases')['href']
        url_documents = BASE_URL + soup.find(id='tab_externalDocuments')['href']
        url_map = BASE_URL + soup.find(id='tab_map')['href']
        address = soup.find('span', {'class': 'address'}).string.strip()
        reference = soup.find('span', {'class': 'caseNumber'}).string.strip()
        proposal = soup.find('span', {'class': 'description'}).string.strip()
        received = datetime.datetime.strptime(
            soup.find(id='simpleDetailsTable').find_all('tr')[1].td.string.strip(),
            "%a %d %b %Y"
        )
        validated = datetime.datetime.strptime(
            soup.find(id='simpleDetailsTable').find_all('tr')[2].td.string.strip(),
            "%a %d %b %Y"
        )
        status = soup.find(id='simpleDetailsTable').find_all('tr')[5].td.span.string.strip()
        results = {
            'proposal': proposal,
            'url': url,
            'url_public_comments': url_public_comments,
            'url_constraints': url_constraints,
            'url_related': url_related,
            'url_documents': url_documents,
            'url_map': url_map,
            'address': address,
            'received': received,
            'validated': validated,
            'status': status,
            'google_maps': "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(address),
            'documents': self.documents(reference)
        }
        return results

    def documents(self, reference):
        params = {
            "SEARCH_TYPE": 1,
            "DOC_CLASS_CODE": "DC",
            "FOLDER1_REF": reference
        }
        r = self.s.get(
            BASE_URL_DOC + "ExternalEntryPoint.aspx",
            params=params,
            stream=True
        )
        results_url = r.url
        r = self.s.get(results_url, params=params, stream=True)
        params['grdResultsP']=1
        result = []
        soup = BeautifulSoup(r.content, 'html.parser')
        body = soup.html.body
        num_documents = int(
            body.find('div', {'class': 'TitleLabel'}).contents[0]
                .split('-')[1].split()[0]
        )
        documents = body.find('table', {'id':'grdResults_tblData'}).find_all('tr', {'class':['AIMRow', 'AIMAltRow']})
        while len(result) < num_documents:
            for doc in documents:
                fields = doc.find_all('td')
                info1 = ''.join(fields[3].contents).strip()
                info2 = ''.join(fields[4].contents).strip()
                d={
                    'url': BASE_URL_DOC + fields[0].a['href'],
                    'date': fields[1].contents[0],
                    'description': fields[2].contents[0].strip(),
                    'info1': info1,
                    'info2': info2
                }
                result.append(d)
            if len(result) < num_documents:
                # Fetch next page before looping round
                params['grdResultsP'] += 1
                r = self.s.get(results_url, params=params, stream=True)
                soup = BeautifulSoup(r.content, 'html.parser')
                documents = soup.html.body.find('table', {'id': 'grdResults_tblData'}).find_all('tr', {'class': ['AIMRow', 'AIMAltRow']})
       
        return result

    def get_document(self, url):
        doc = self.s.get(url)
        final_url = doc.history[0].headers['Location']
        filename = final_url[final_url.rfind('/')+1:]
        response = {
            'final_url': doc.history[0].headers['Location'],
            'filename': filename,
            'content': doc.content
        }
        return response

if __name__ == "__main__":
    p = Planning()
    if False:
        # The application below has more than 25 documents,
        # and requires multiple index page fetches.
        documents = p.documents('DC/19/1906/FUL')
        pprint(documents)
    if False:
        document = p.get_document('http://publicaccessdocuments.eastsuffolk.gov.uk/AniteIM.WebSearch/Download.aspx?ID=1480471')
        pprint(document)
    if True:
        pprint(p.get_application('DC/19/1906/FUL'))
