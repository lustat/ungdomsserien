import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import datetime
from definitions import DATA_DIR
from loader.read_results import get_events, get_event


def get_runner_data(person_id=64322, apikey=None):
    # person_id = '99847' # Exempel-ungdom
    #
    # person_id = '64322'  # Exempel skof-ledare
    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(person_id, str):
        person_id = str(person_id)

    headers = {'ApiKey': apikey}

    # response = requests.get('https://eventor.orientering.se/api/results/person/', headers=headers, params=params)
    # root = ET.fromstringlist(response.text)
    # return root


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
    persons = persons.loc[persons.sex == sex]
    return persons


def get_runner_participation(id='99847', apikey=None):
    data_path = DATA_DIR + '/runner_data/'
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    if apikey is None:
        apikey = os.environ["apikey"]

    if not isinstance(id, str):
        id = str(id)

    file_path = data_path + '/' + id + '.parq'

    if os.path.isfile(file_path):
        competitions = pd.read_parquet(file_path)
        return competitions

    from_date = datetime.datetime.now() - datetime.timedelta(days=100)
    from_date_str = from_date.strftime('%Y-%m-%d') + ' 00:00:00'

    headers = {'ApiKey': apikey}
    params = {'personId': id, 'includeSplitTimes': 'false', 'fromDate': from_date_str}

    response = requests.get('https://eventor.orientering.se/api/results/person', headers=headers, params=params)
    root = ET.fromstringlist(response.text)
    competitions = pd.DataFrame()
    for result_list in root.findall('ResultList'):
        class_name = result_list.find('ClassResult').find('EventClass').find('Name').text
        event_type = int(result_list.find('Event').find('EventClassificationId').text)
        include_class = is_competition_class(class_name)
        include_event = is_competition(event_type)

        if include_class & include_event:
            if result_list.find('ClassResult').find('PersonResult') is not None:
                person = result_list.find('ClassResult').find('PersonResult').find('Person').find('PersonName')
                runner = person.find('Given').text + ' ' + person.find('Family').text
                event_name = result_list.find('Event').find('Name').text
                event_id = int(result_list.find('Event').find('EventId').text)
                date = result_list.find('Event').find('StartDate').find('Date').text

                competitions.at[event_id, 'runner'] = runner
                competitions.at[event_id, 'event_name'] = event_name
                competitions.at[event_id, 'class_name'] = class_name
                competitions.at[event_id, 'date'] = date

    competitions = competitions.reset_index(drop=False).rename(columns={'index': 'event_id'})
    competitions.to_parquet(file_path)

    return competitions


def get_runners_participation(ids=None):
    if ids is None:
        # ids = [99847, 135147, 148254, 110483, 145811, 105821, 105822, 135150, 121897, 162282, 114463, 126502]
        ids = [135150, 99847, 110483, 94497, 105822, 105821, 61254, 135147, 148254, 126502, 114463, 145811, 162282, 121897, \
               162503, 132573, 86261, 196346]

    df_list = []
    for id in ids:
        df = get_runner_participation(id=id)
        df_list.append(df)

    runs = pd.concat(df_list, axis=0)
    return runs


def get_runners_per_class(df):
    groupby_columns = ['event_id', 'event_name', 'class_name', 'date']
    columns = ['runner'] + groupby_columns
    events = df[columns].groupby(by=groupby_columns).count()
    events = events.reset_index(drop=False)

    events = events.sort_values(by='date')
    print(events)
    return events


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


def identify_relevant_classes(comps, inpath):
    races = []
    for key, row in comps.iterrows():
        df = get_event(row.event_id, inpath)
        if df.empty:
            print('No data for event ' + str(row.event_id))
        else:
            race = df.loc[df.classname == row.class_name]
            race = race.assign(event_name=row.event_name)
            if not race.empty:
                races.append(race)

    return races


def races_to_excel(races: pd.DataFrame, outpath: str):
    if not os.path.isdir(outpath):
        os.makedirs(outpath)
    excel_file = outpath + '/results.xlsx'

    empty_row = pd.DataFrame(columns=races[0].columns, index=[0])
    name_row = pd.DataFrame(columns=races[0].columns, index=[0])

    extended_list = []
    for race in races:
        name_row.at[0, 'name'] = race.event_name.iloc[0]
        filtered_race = race.loc[(race.region == 16) & race.started]
        filtered_race = filtered_race.assign(minutes=round(race.seconds/60, 2))

        extended_list.append(pd.concat([empty_row, name_row, filtered_race], axis=0, sort=False))

    df_out = pd.concat(extended_list, axis=0, sort=False)

    column_order = ['name', 'event_year', 'event_date', 'classname', 'personid', 'birthyear', 'age',  'club',
                    'finished', 'position', 'minutes']

    df_out[column_order].to_excel(excel_file, index=False)
    return excel_file


if __name__ == '__main__':
    pd.set_option('max_columns', 20)
    pd.set_option('display.width', 400)
    partic = get_runners_participation()
    competitons = get_runners_per_class(partic)

    storage_path = DATA_DIR + '/events'
    # get_events(storage_path, event_list=competitons.event_id.unique())

    output_path = DATA_DIR + '/identified_races'
    results = identify_relevant_classes(competitons, inpath=storage_path)
    races_to_excel(results, outpath=output_path)

    # raw = get_members_in_organisation()
    # runners = get_age_group(raw, birth_year_interval=(2007, 2008))
    # runners = pick_gender(runners, 'M')
    # get_runner_results(runners.index[0], apikey=None)
    # print(runners)