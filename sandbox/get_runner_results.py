import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import datetime


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

    from_date = datetime.datetime.now() - datetime.timedelta(days=400)
    from_date_str = from_date.strftime('%Y-%m-%d') + ' 00:00:00'

    headers = {'ApiKey': apikey}
    params = {'personId': id, 'includeSplitTimes': False, 'top': 10, 'fromDate': from_date_str}

    if not isinstance(id, str):
        id = str(id)

    response = requests.get('https://eventor.orientering.se/api/results/person', headers=headers, params=params)
    root = ET.fromstringlist(response.text)
    for result_list in root.findall('ResultList'):
        # print(result_list.getchildren())
        class_name = result_list.find('ClassResult').find('EventClass').find('Name').text
        event_type = int(result_list.find('Event').find('EventClassificationId').text)
        include_class = is_competition_class(class_name)
        include_event = is_competition(class_name)

        if include_class & include_event:
            print(int(result_list.find('Event').find('EventId').text))
            print(class_name)
            for t in result_list.find('ClassResult').findall('PersonResult'):
                for x in t.itertext():
                    print(x)


def is_competition(event_classification_id):
    """ 1=mästerskapstävling, 2=nationell tävling, 3=distriktstävling, 4=närtävling, 5=klubbtävling,
    6=internationell tävling.

    """
    is_not_local = False
    if (event_classification_id < 3) | (event_classification_id > 4):
        is_not_local = True

    return is_not_local


def is_competition_class(event_class_name):
    is_competition = False
    if len(event_class_name) == 3:
        if event_class_name.lower().startswith('h') | event_class_name.lower().startswith('d'):
            is_competition = True

    return is_competition

if __name__ == '__main__':
    raw = get_members_in_organisation()
    runners = get_age_group(raw, birth_year_interval=(2007, 2008))
    runners = pick_gender(runners, 'M')
    get_runner_results(runners.index[0], apikey=None)
    print(runners)