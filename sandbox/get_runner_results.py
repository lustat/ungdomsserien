import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def get_members_in_organisation(id=125, apikey=None):
    # SKOF = 16
    # HSOK = 125
    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(id, str):
        id = str(id)

    headers = {'ApiKey': apikey}

    '{id}'
    # response = requests.get('https://eventor.orientering.se/api/organisation/' + id, headers=headers)
    response = requests.get('https://eventor.orientering.se/api/persons/organisations/' + id, headers=headers)
    root = ET.fromstringlist(response.text)
    return root


def get_age_group(root, birth_year):
    for t in root.itertext():
        print(t)




def get_runner_results(id, apikey=None):
    if apikey is None:
        apikey = os.environ["apikey"]

    headers = {'ApiKey': apikey}

    if not isinstance(id, str):
        id = str(id)


    response = requests.get('https://eventor.orientering.se/api/results/person/', headers=headers)
    root = ET.fromstringlist(response.text)
    obj_name = root.find('Name')
    if obj_name is None:
        event_name = 'Okänt namn'
    else:
        event_name = obj_name.text

    event_date = root.find('StartDate/Date')
    if event_date is None:
        event_year = 'Year?'
    else:
        date = datetime.strptime(event_date.text, '%Y-%m-%d')
        event_year = date.year

    return event_name, event_year


if __name__ == '__main__':
    raw = get_members_in_organisation()
    persons = get_age_group(raw, birth_year=(2007, 2008))
