# Search -> Application
# Application -> Metadata and documents
# Document -> Metadata and contents

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

class Parish(enum.Enum):
    ALDEBURGH = 'ALDE'
    ALDERTON = 'ALDN'
    ALDRINGHAM_CUM_THORPE='ALDR'
    BADINGHAM='BADI'
    BARNBY='BARNBY'
    BARSHAM='BARSHA'
    BAWDSEY='BAWD'
    BECCLES='BECCLE'
    BENACRE='BENACR'
    BENHALL='BENH'
    BLAXHALL='BLAX'
    BLUNDESTON='BLUNDE'
    BLYFORD='BLYFOR'
    BLYTHBURGH='BLYT'
    BOULGE='BOUL'
    BOYTON='BOYT'
    BRAMFIELD='BRAM'
    BRAMPTON_WITH_STOVEN='BRANST'
    BRANDESTON='BRAN'
    BREDFIELD='BRED'
    BRIGHTWELL='BRIG'
    BROMESWELL='BROM'
    BRUISYARD='BRUI'
    BUCKLESHAM='BUCK'
    BUNGAY='BUNGAY'
    BURGH='BURG'
    BUTLEY='BUTL'
    CAMPSEA_ASHE='CAMP'
    CAPEL_ST_ANDREW='CAPE'
    CARLTON_COLVILLE='CARCOL'
    CHARSFIELD='CHAR'
    CHEDISTON='CHED'
    CHILLESFORD='CHIL'
    CLOPTON='CLOP'
    COOKLEY='COOK'
    CORTON='CORTON'
    COVEHITHE='COVEN'
    CRANSFORD='CRAN'
    CRATFIELD='CRAT'
    CRETINGHAM='CRET'
    CULPHO='CULP'
    DALLINGHOO='DALL'
    DARSHAM='DARS'
    DEBACH='DEBA'
    DENNINGTON='DENN'
    DUNWICH='DUNW'
    EARL_SOHAM='EARL'
    EASTON='EAST'
    ELLOUGH='ELLOU'
    EYKE='EYKE'
    FALKENHAM='FALK'
    FARNHAM='FARN'
    FELIXSTOWE='FELX'
    FLIXTON_EAST='FLEAST'
    FLIXTON_WEST='FLWEST'
    FOXHALL='FOXH'
    FRAMLINGHAM='FRAM'
    FRISTON='FRIS'
    FROSTENDEN='FROSTE'
    GEDGRAVE='GEDG'
    GISLEHAM='GISLEH'
    GREAT_BEALINGS='GRBL'
    GREAT_GLEMHAM='GRGM'
    GRUNDISBURGH='GRUN'
    HACHESTON='HACH'
    HALESWORTH='HALESW'
    HASKETON='HASK'
    HEMLEY='HEML'
    HENSTEAD_WITH_HULVER_STREET='HENHUL'
    HEVENINGHAM='HEVE'
    HOLLESLEY='HOLL'
    HOLTON='HOLTON'
    HOMERSFIELD='HOMERS'
    HOO='HOO'
    HUNTINGFIELD='HUNT'
    IKEN='IKEN'
    ILKETSHALL_ST_ANDREW='ILKSAN'
    ILKETSHALL_ST_JOHN='ILKSJO'
    ILKETSHALL_ST_LAWRENCE='ILKSLA'
    ILKETSHALL_ST_MARGARET='ILKSMA'
    KELSALE_CUM_CARLTON='KELS'
    KESGRAVE='KESG'
    KESSINGLAND='KESSIN'
    KETTLEBURGH='KETT'
    KIRTON='KIRT'
    KNODISHALL='KNOD'
    LEISTON_CUM_SIZEWELL='LEIS'
    LETHERINGHAM='LETH'
    LEVINGTON='LEVI'
    LINSTEAD_MAGNA='LNMG'
    LINSTEAD_PARVA='LNPV'
    LITTLE_BEALINGS='LTBL'
    LITTLE_GLEMHAM='LIGL'
    LOUND='LOUND'
    LOWESTOFT='LWTOFT'
    MARLESFORD='MARL'
    MARTLESHAM='MART'
    MELTON='MELT'
    METTINGHAM='METTIN'
    MIDDLETON='MIDD'
    MONEWDEN='MONE'
    MUTFORD='MUTFOR'
    NACTON='NACT'
    NEWBOURNE='NEWB'
    NORTH_COVE='NTHCOV'
    ORFORD='ORFO'
    OTLEY='OTLE'
    OULTON='OULTON'
    OULTON_BROAD='OBROAD'
    PARHAM='PARH'
    PEASENHALL='PEAS'
    PETTISTREE='PETT'
    PLAYFORD='PLAY'
    PURDIS_FARM='PURD'
    RAMSHOLT='RAMS'
    REDISHAM='REDISH'
    RENDHAM='REND'
    RENDLESHAM='RENL'
    REYDON='REYDON'
    RINGSFIELD='RINGSF'
    RUMBURGH='RUMBUR'
    RUSHMERE='RUSHME'
    RUSHMERE_ST_ANDREW='RUSH'
    SAXMUNDHAM='SAXM'
    SAXTEAD='SAXT'
    SHADINGFIELD='SHADIN'
    SHIPMEADOW='SHIPME'
    SHOTTISHAM='SHOT'
    SIBTON='SIBT'
    SNAPE='SNAP'
    SOMERLEYTON_ASHBY_AND_HERRINGFLEET='ASHERS'
    SOTHERTON='SOTHER'
    SOTTERLEY='SOTTER'
    SOUTH_COVE='STHCOV' 
    SOUTH_ELMHAM_ALL_SAINTS_AND_ST_NICHOLAS='SEASSN'
    SOUTH_ELMHAM_ST_CROSS='SESCRO'
    SOUTH_ELMHAM_ST_JAMES='SESJAM'
    SOUTH_ELMHAM_ST_MARGARET='SESMAR'
    SOUTH_ELMHAM_ST_MICHAEL='SESMIC'
    SOUTH_ELMHAM_ST_PETER='SESPET'
    SOUTHWOLD='STHWOL'
    SPEXHALL='SPEXHA'
    STERNFIELD='STER'
    STRATFORD_ST_ANDREW='STRA'
    STRATTON_HALL='STRH'
    SUDBOURNE='SUDB'
    SUTTON='SUTT'
    SUTTON_HEATH='SU'
    SWEFFLING='SWEF'
    SWILLAND='SWIL'
    THEBERTON='THEB'
    THORINGTON='THOR'
    TRIMLEY_ST_MARTIN='TMAT'
    TRIMLEY_ST_MARY='TMRY'
    TUDDENHAM_ST_MARTIN='TUDD'
    TUNSTALL='TUNS'
    UBBESTON='UBBE'
    UFFORD='UFFO'
    UGGESHALL='UGGESH'
    WALBERSWICK='WALB'
    WALDRINGFIELD='WALD'
    WALPOLE='WALP'
    WANGFORD_AND_HENHAM='WANHEN'
    WANTISDEN='WANT'
    WENHASTON='WENH'
    WESTERFIELD='WESF'
    WESTHALL='WESTHA'
    WESTLETON='WESL'
    WESTON='WESTON'
    WICKHAM_MARKET='WICK'
    WILLINGHAM='WILSMA'
    WISSETT='WISSET'
    WITNESHAM='WITN'
    WOODBRIDGE='WOOD'
    WORLINGHAM='WORLIN'
    WRENTHAM='WRENTH'
    YOXFORD='YOXF'

class Ward(enum.Enum):
    ALDEBURGH_AND_LEISTON='ALDLEI'
    BECCLES_AND_WORLINGHAM='BECWOR'
    BUNGAY_AND_WAINFORD='BUNWAI'
    CARLFORD_AND_FYNN_VALLEY='CARFYN'
    CARLTON_AND_WHITTON='CARWHI'
    CARLTON_COLVILLE='CARCLL'
    DEBEN='DEBEN'
    FELIXSTOWE_EAST='FELEAS'
    FELIXSTOWE_WEST='FELWES'
    FRAMLINGHAM='FRAMLI'
    GUNTON_AND_ST_MARGARETS='GUNSTM'
    HALESWORTH_AND_BLYTHING='HALBLY'
    HARBOUR_AND_NORMANSTON='HARNOR'
    KELSALE_AND_YOXFORD='KELYOX'
    KESGRAVE='KESGRA'
    KESSINGLAND='KESS'
    KIRKLEY_AND_PAKEFIELD='KIRPAK'
    LOTHINGLAND='LOTHN'
    MARTLESHAM_AND_PURDIS_FARM='MARPUR'
    MELTON='MELTON'
    ORWELL_AND_VILLAGES='ORWELL'
    OULTON_BROAD='OULBRO'
    RENDLESHAM_AND_ORFORD='RENORF'
    RUSHMERE_ST_ANDREW='RUSHST'
    SAXMUNDHAM='SAXMUN'
    SOUTHWOLD='SOUTHW'
    WICKHAM_MARKET='WICMAR'
    WOODBRIDGE='WOODBR'
    WRENTHAM_WANGFORD_AND_WESTLETON='WRWAWE'

class Planning():
    def __init__(self):
         self.s = requests.Session()       

    def search(self, start_date, end_date, parish='', ward=''):
        "Search planning portal for relevant applications"
        query = {
            'searchCriteria.reference': '',
            'searchCriteria.planningPortalReference': '',
            'searchCriteria.alternativeReference': '',
            'searchCriteria.description': '',
            'searchCriteria.applicantName': '',
            'searchCriteria.caseType': '',
            'searchCriteria.ward': ward,
            'searchCriteria.parish': parish,
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
            'date(applicationValidatedStart)': start_date.strftime(r"%d/%m/%Y"),
            'date(applicationValidatedEnd)': end_date.strftime(r"%d/%m/%Y"),
            'date(applicationCommitteeStart)': '',
            'date(applicationCommitteeEnd)': '',
            'date(applicationDecisionStart)': '',
            'date(applicationDecisionEnd)': '',
            'date(appealDecisionStart)': '',
            'date(appealDecisionEnd)': '',
            'searchType': 'Application'
        }
        url = BASE_URL + '/online-applications/advancedSearchResults.do?action=firstPage'
        self.s.post(url, data=query, stream=True)
        r2 = self.s.post(
            BASE_URL + '/online-applications/pagedSearchResults.do',
            data={
                'searchCriteria.page': 1,
                'action': 'page',
                'orderBy': 'DateReceived',
                'orderByDirection': 'Descending',
                'searchCriteria.resultsPerPage': '100'
            },
            stream=True
        )
        soup = BeautifulSoup(r2.content, 'html.parser')
        results = {}
        for i in soup.find(id='searchresults').find_all('li'):
            url = BASE_URL + i.a.get('href')
            address = i.find('p', {'class': 'address'}).string.strip()
            metainfo = i.find('p', {'class': 'metaInfo'}).contents
            reference = metainfo[0].strip().split(':')[1].strip()
            received = datetime.datetime.strptime(
                metainfo[2].strip().split(':')[1].strip(),
                "%a %d %b %Y"
            )
            validated = datetime.datetime.strptime(
                metainfo[4].strip().split(':')[1].strip(),
                "%a %d %b %Y"
            )
            results[reference] = {
                'proposal': i.a.string.strip(),
                'url': url,
                'url_public_comments': url.replace('summary', 'neighbourComments'),
                'url_constraints': url.replace('summary', 'constraints'),
                'url_related': url.replace('summary', 'relatedCases'),
                'url_documents': url.replace('summary', 'externalDocuments'),
                'url_map': url.replace('summary', 'map'),
                'address': address,
                'received': received,
                'validated': validated,
                'status': metainfo[6].strip().split(':')[1].strip(),
                'google_maps': "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(address)
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
        applications = p.search(
            Parish.LOWESTOFT,
            start_date=datetime.date(2019, 5, 5),
            end_date=datetime.date(2019, 5, 16)
        )
        pprint(applications)
    if True:
        # The application below has more than 25 documents,
        # and requires multiple index page fetches.
        documents = p.documents('DC/19/1906/FUL')
        pprint(documents)
    if False:
        document = p.get_document('http://publicaccessdocuments.eastsuffolk.gov.uk/AniteIM.WebSearch/Download.aspx?ID=1480471')
        pprint(document)

    if False:
        applications = p.search(
            Parish.LOWESTOFT,
            Ward.HARBOUR_AND_NORMANSTON,
            start_date=datetime.date(2019, 5, 5),
            end_date=datetime.date(2019, 5, 16)
        )
        for ref, data in applications.items():
            print(ref)
            dir_name = ref.replace('/', '_')
            os.mkdir(dir_name)
            documents = p.documents(ref)
            for i in documents:
                print(i)
                print(i['description'])
                document = p.get_document(i['url'])
                filename = os.path.join(dir_name, document['filename'])
                with open(filename, 'wb') as f:
                    f.write(document['content'])

