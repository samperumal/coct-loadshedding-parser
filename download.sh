#!/bin/bash
#curl "https://www.capetown.gov.za/Family%20and%20home/Residential-utility-services/Residential-electricity-services/Load-shedding-and-outages" > latest.html
cd /home/pi/loadshed
source .venv/bin/activate
python parse.py >> download.log
