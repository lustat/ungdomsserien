import os
import pandas as pd
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


def get_age_group(root, birth_year_interval):
    persons = pd.DataFrame()
    for t in root.findall('Person'):
        birth_year = int(t.find('BirthDate').find('Date').text[:4])
        if (birth_year >= birth_year_interval[1]) & (birth_year <= birth_year_interval[1]):
            name = t.find('PersonName').find('Given').text + ' ' + t.find('PersonName').find('Family').text
            id = int(t.find('PersonId').text)
            sex = t.get('sex')
            persons.at[id, 'name'] = name
            persons.at[id, 'birth_year'] = int(birth_year)
            persons.at[id, 'sex'] = sex

    persons = persons.assign(birth_year=persons.birth_year.astype(int))
    return persons


def pick_gender(persons, sex='M'):
    persons = persons.loc[persons.sex==sex]
    return persons


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
    runners = get_age_group(raw, birth_year_interval=(2007, 2008))
    runners = pick_gender(runners, 'M')
    get_runner_results(runners.index[0], apikey=None)
    print(runners)