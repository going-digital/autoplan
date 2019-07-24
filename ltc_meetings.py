import requests
from bs4 import BeautifulSoup
import datetime
import re

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

print(meetings)
