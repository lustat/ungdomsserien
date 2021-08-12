import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import datetime


def get_runner_data(person_id=64322, apikey=None):
    # person_id = '99847' # Exempel-ungdom
    #
    # person_id = '64322'  # Exempel skof-ledare
    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(person_id, str):
        person_id = str(person_id)

    headers = {'ApiKey': apikey}

    response = requests.get('https://eventor.orientering.se/api/results/person/', headers=headers, params=params)
    root = ET.fromstringlist(response.text)
    return root

def get_members_in_organisation(id=16, apikey=None):
    # SKOF = 16
    # HSOK = 125
    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(id, str):
        id = str(id)

    headers = {'ApiKey': apikey}

    response = requests.get('https://eventor.orientering.se/api/persons/organisations/' + id, headers=headers)
    root = ET.fromstringlist(response.text)
    return root


def get_age_group(root, birth_year_interval):
    persons = pd.DataFrame()
    for t in root.findall('Person'):
        birth_year = int(t.find('BirthDate').find('Date').text[:4])
        name = t.find('PersonName').find('Given').text + ' ' + t.find('PersonName').find('Family').text
        print(name)
        if (birth_year >= birth_year_interval[1]) & (birth_year <= birth_year_interval[1]):

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


def get_runner_results(id='99847', apikey=None):
    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(id, str):
        id = str(id)

    from_date = datetime.datetime.now() - datetime.timedelta(days=400)
    from_date_str = from_date.strftime('%Y-%m-%d') + ' 00:00:00'

    headers = {'ApiKey': apikey}
    params = {'personId': id, 'includeSplitTimes': False, 'top': 5, 'fromDate': from_date_str}

    response = requests.get('https://eventor.orientering.se/api/results/person', headers=headers, params=params)
    root = ET.fromstringlist(response.text)
    competitions = pd.DataFrame()
    for result_list in root.findall('ResultList'):
        class_name = result_list.find('ClassResult').find('EventClass').find('Name').text
        event_type = int(result_list.find('Event').find('EventClassificationId').text)
        include_class = is_competition_class(class_name)
        include_event = is_competition(event_type)

        if include_class & include_event:
            person = result_list.find('ClassResult').find('PersonResult').find('Person').find('PersonName')
            runner = person.find('Given').text + ' ' + person.find('Family').text
            event_name = result_list.find('Event').find('Name').text
            event_id = int(result_list.find('Event').find('EventId').text)

            competitions.at[event_id, 'runner'] = runner
            competitions.at[event_id, 'event_name'] = event_name
            competitions.at[event_id, 'class_name'] = class_name

    competitions = competitions.reset_index(drop=False).rename(columns = {'index': 'event_id'})
    return competitions


def get_runners_results(ids=None):
    if ids is None:
        ids = [135147, 148254, 110483, 145811, 99847, 105821, 105822, 135150, 121897, 162282, 114463, 126502]

    df_list = []
    for id in ids:
        df = get_runner_results(id=id)
        df_list.append(df)

    runs = pd.concat(df_list, axis=0)
    return runs


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
    pd.set_option('max_columns', 10)
    raw_results = get_runner_results()
    # raw_results = get_runners_results()
    print(raw_results)
    print(raw_results)
    # raw = get_members_in_organisation()
    # runners = get_age_group(raw, birth_year_interval=(2007, 2008))
    # runners = pick_gender(runners, 'M')
    # get_runner_results(runners.index[0], apikey=None)
    # print(runners)