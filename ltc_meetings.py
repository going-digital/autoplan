import requests
from bs4 import BeautifulSoup
import datetime
import re
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

def get_meetings():
    r1 = requests.get("https://lowestofttowncouncil.gov.uk/about-the-council/meetings/")
    soup = BeautifulSoup(r1.text)
    table = soup.body.find('div', {'id': 'standardPage'}).table.find_all('tr')

    meetings = []
    for row in table:
        columns = row.find_all('td')
        mtg_type = columns[0].text.strip()
        if (mtg_type == 'Planning and Environment Committee'):
            date = columns[1].text.strip() + ' ' + columns[2].text.strip()
            date = re.sub(r"(\d+)(st|nd|rd|th)",r"\1", date)
            date = datetime.datetime.strptime(date, "%d %B %Y %H:%M")
            meetings.append({
                'group': columns[0].text.strip(),
                'date': date,
                'documents': columns[3].find_all('a')
            })
    return meetings

def pdf_to_txt(pdf_fp):
    parser = PDFParser(pdf_fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.char_margin = 1.0
    laparams.word_margin = 1.0
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    extracted_text = ''
    for page in doc.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                extracted_text += lt_obj.get_text()
    return extracted_text

def extract_applications(text):
    # Find strings of the form AA/11/1111/AAA
    return re.findall(r".{2}/\d{2}/\d{4}/.{3}", extracted_text)

# TODO: Find latest planning agenda
# TODO: Download planning agenda, pdf_to_txt and extract_applications
# TODO: Integrate