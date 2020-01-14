import requests
import csv
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/2019_in_spaceflight"

# TODO - handle response error here
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table", {"class": "wikitable collapsible"})

k = 0
for i,table in enumerate(tables):
    prev_h2 = table.find_previous_sibling("h2")
    if prev_h2.span.string == "Orbital launches":
        k = i
        break

orbital_table = tables[k]

ths = orbital_table.find_all("th")

headings = [th.text.strip() for th in ths]
header_rowspan = int(ths[0]["rowspan"])

# deal with content
rsp = 1
i = 0
orbital_launches = {}

# generate date time
start = datetime.strptime("01-01-2019", "%d-%m-%Y")
end = datetime.strptime("31-12-2019", "%d-%m-%Y")
date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)]

for date in date_generated:
    date = date.isoformat() + "+00:00"
    orbital_launches[date] = 0

trs = orbital_table.find_all("tr")
n = len(trs)
while i < n:
    # skip table header
    if i < header_rowspan:
        i += 1
        continue

    tds = trs[i].find_all("td")

    # no column
    if not tds:
        i += 1
        continue

    # skip Month header row
    # cannot scrape every month directly so use <li> to help
    should_skip = False
    for td in tds:
        if len(td.select("li")) > 0 or len(td.select("h3")) > 0 or len(td.select('table')) > 0:
            should_skip = True

    if should_skip:
        i += 1
        continue
    # extract information for the next k (rowspan) rows --> skip rocket info
    rsp = int(tds[0]["rowspan"]) if tds[0].has_attr("rowspan") else 1
    is_launch_work = False

    # get the date and format it as 01 January 2019 00:00:00
    launch_date = trs[i].find_all("td")[0].span.text.strip().split(" ")
    if int(launch_date[0]) < 10:
        launch_date[0] = "0" + launch_date[0]

    # handle Month[][] with super script
    if "[" in launch_date[1]:
        date_str = launch_date[1].split("[")
        launch_date[1] = date_str[0]

    date = launch_date[0] + " " + launch_date[1] + " 2019 00:00:00 +0000"
    date = datetime.strptime(date, "%d %B %Y %H:%M:%S %z").isoformat()
    # orbital_launches[date] = 0

    scrape_bound = i+rsp+1 if i+rsp < n else n
    for k in range(i+1, scrape_bound):
        tds = trs[k].find_all('td')
        if tds[0].has_attr("colspan"):
            # skip remark
            if tds[0]["colspan"] == 6:
                continue
        else:
            payload_outcome = tds[-1].text.strip().lower()
            if "operational" in payload_outcome or "en route" in payload_outcome or "successful" in payload_outcome:
                is_launch_work = True

    if is_launch_work:
        orbital_launches[date] += 1

    i += rsp

# export to CSV
# print(orbital_launches)
result_file_name = 'orbital_launches.csv'
csv_columns = ['date', 'value']

try:
    with open(result_file_name, 'w',newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['date','value'])
        for key,val in orbital_launches.items():
            writer.writerow([key,val])
except IOError:
    print("I/O error")













