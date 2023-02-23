import json
import re
from datetime import datetime as dt, timedelta
from dateutil.parser import parse

scraped_filename = 'cpt-input.txt'
override_filename = 'cpt-override.txt'
hashname = 'cpt-input.md5'

def hash_file(filename):

    import hashlib
    
    with open(filename,"rb") as f:
        bytes = f.read() # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest()
        return readable_hash

def hash_input():
  return hash_file(filename)


def get_filename():
  try:
    with open(scraped_filename + '.md5', 'r') as h:
      override_hash = h.readline().strip()

    scraped_hash = hash_file(scraped_filename)

    if override_hash == scraped_hash:
      print(dt.now(), 'Using override', scraped_filename, override_hash, scraped_hash)
      return override_filename
  except:
    pass

  return scraped_filename

url = 'https://www.capetown.gov.za/Family%20and%20home/Residential-utility-services/Residential-electricity-services/Load-shedding-and-outages'

def scrape_input():
    import requests
    from bs4 import BeautifulSoup

    html_text = requests.get(url).text.replace("</br>", "")
    soup = BeautifulSoup(html_text, 'html.parser')
    result = soup.find('div', { 'class': 'section-pull' }).find("p")
    # print(result.getText())

    with open(scraped_filename, 'w') as o:
        print(result.text, file = o)

def get_cpt_input():
  with open(filename, "r") as f:
    return f.readlines()

def parse_cpt_input(lines):
  last_date = dt.utcnow().date()
  stages = []
  for line in lines:
    stage_match = re.match(r'Stage (\d+): (\d+:\d+) - (\d+:\d+)', line)
    date_match = re.match(r'([0-9]+) (\w+)', line)

    if stage_match is not None:
      start_time = dt.combine(last_date, parse(stage_match[2]).time())
      end_time = dt.combine(last_date, parse(stage_match[3]).time())
      if end_time <= start_time:
        end_time += timedelta(1)
      stages.append({
        "stage": int(stage_match[1]), 
        "start": start_time.isoformat(), 
        "end": end_time.isoformat()
        })
    elif date_match is not None:
      last_date = parse(date_match[0])

  return stages

def writeBlob(key):
    from azure.storage.blob import BlobServiceClient, ContentSettings

    service = BlobServiceClient(account_url="https://cptloadshed.blob.core.windows.net/", credential=key)

    blob = service.get_blob_client("stage", "current.json")

    data = {
        "Cape Town": {
          "stages": parse_cpt_input(get_cpt_input()), #city_sites.parseCpt(),
          "url": "https://www.capetown.gov.za/Family%20and%20home/Residential-utility-services/Residential-electricity-services/Load-shedding-and-outages",
          "site": "CoCT",
          "time": dt.strftime(dt.now(), "%H:%M, %Y-%m-%d")
        },
        "Johannesburg": None, #city_sites.parseJhb(),
        "Durban": None,
        "Tshwane (Pretoria)": None, #city_sites.parsePta()
    }

    with open("current.json", "w") as fout:
        print(json.dumps(data, indent=2), file = fout)

    with open("current.json", "rb") as fin:
        blob.upload_blob(fin, overwrite = True)
        blob.set_http_headers(ContentSettings(content_type = "application/json"))

    print(dt.now(), "Successfully wrote blob")

def parse_input(filename):
    current_hash = hash_file(filename)
    previous_hash = ""

    try:
        with open(hashname, 'r') as h:
            previous_hash = h.readline().strip()
    except:
        pass

    if previous_hash != current_hash:
        with open("key.txt", "r") as key_file:
            key = key_file.read()
            writeBlob(key)

        # print('Updating hash', previous_hash, current_hash)
        with open(hashname, 'w') as h:
            print(current_hash, file = h)

        import shutil
        shutil.copy2(filename, 'archive/' + dt.now().strftime('%Y-%m-%d %H-%M-%S ') + filename)
    else:
        print(dt.now(), 'No update required')


if __name__ == "__main__":    
    scrape_input()
    filename = get_filename()
    parse_input(filename)
