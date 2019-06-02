import tqdm
import planning_portal
import jinja2
import datetime
from pprint import pprint

meeting_date = datetime.date(2019, 5, 28)
reference_list = [
    'DC/19/1966/FUL',
    'DC/19/1848/FUL',
    'DC/19/1951/FUL',
    'DC/19/1950/FUL',
    'DC/19/1906/FUL',
]
output_file = "test3.html"

p = planning_portal.Planning()

applications = {}
    
run_date = datetime.datetime.now()

# Fetch applications
for reference in tqdm.tqdm(reference_list, desc='Fetching applications', ascii=True):
    applications[reference] = p.get_application(reference)

# Build report
templateLoader = jinja2.FileSystemLoader(searchpath='./')
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = 'template.html.j2'
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(
    title='Planning notes',
    parish='Lowestoft',
    run_date=run_date,
    meeting_date=meeting_date,
    applications=applications,
)
with open(output_file, 'w') as f:
    f.write(outputText)
