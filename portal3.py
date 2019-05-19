import portal2
import datetime
import jinja2
import tqdm

parish = portal2.Parish.LOWESTOFT.value
#start_date=datetime.date(2019, 5, 5)
#end_date=datetime.date(2019, 5, 16)
start_date = datetime.date(2019, 4, 13)
end_date = datetime.date(2019, 5, 6)
run_date = datetime.datetime.now()

output_file = "test.html"

p = portal2.Planning()

# Get list of planning applications
applications = p.search(start_date, end_date, parish=parish)

# Get list of documents for each application
for reference, application in tqdm.tqdm(applications.items()):
    application['documents'] = p.documents(reference)[1]

# Generate document
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "template.html.j2"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(
    title='Planning notes',
    parish='Lowestoft',
    start_date=start_date,
    end_date=end_date,
    run_date=run_date,
    applications=applications
)
with open(output_file, 'w') as f:
    f.write(outputText)
