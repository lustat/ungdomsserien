import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from loader.loader_utils import included_class
from calculation.points_calculation import add_points_to_event, add_night_points_to_event
from calculation.summarize import individual_summary, club_summary, sort_based_on_division
from datetime import datetime
from output.create_excel import individual_results_excel, club_results_to_excel
from loader.club_to_region import get_parent_org_quick
from calculation.calc_utils import add_manual_night_runners, clean_division_input
from loader.read_manual_excel import read_manual_input
from loader.loader_utils import get_event_name
from joblib import Parallel, delayed
import multiprocessing


def get_events(storage_path, event_list, apikey=None, parallel_flag=False):

    if not os.path.exists(storage_path):
        print(storage_path + ' skapas')
        os.makedirs(storage_path)

    number_of_cores = multiprocessing.cpu_count()
    if parallel_flag and (number_of_cores > 2):
        Parallel(n_jobs=number_of_cores-1, batch_size=1, verbose=0)(
            delayed(get_event)(event, storage_path, apikey) for event in event_list)
    else:
        for event in event_list:
            get_event(event, storage_path, apikey)


def get_event(event_id, storage_path, apikey=None, debugmode=False):
    if apikey is None:
        apikey = os.environ["apikey"]

    output_file = os.path.join(storage_path, str(event_id) + '.csv')
    if not os.path.exists(output_file):  # Load events
        url = "https://eventor.orientering.se/api/results/event"

        headers = {'ApiKey': apikey}
        response = requests.get(url, headers=headers, params={'eventId': event_id, 'includeSplitTimes': False})
        root = ET.fromstringlist(response.text)
        df = get_resultlist(root, apikey, debugmode)
        if not df.empty:
            # # TODO simulate an empty df
            # if str(event_id) == '21961':
            #     print('THIS IS A TEST RUN. REMOVE THIS LINE')
            #     return pd.DataFrame()
            if sum(df.finished) > 0:
                print('Sparar resultat: ' + output_file)
                df.to_csv(output_file, index=False)
            else:
                df = pd.DataFrame()
    else:  # Load already stored event
        print('Läser in lokal fil: ' + str(output_file))
        df = pd.read_csv(output_file)
    return df


def evaluate(storage_path, event_list, apikey, event_to_manual):

    for event in event_list:
        output_file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        unidentified_file = os.path.join(storage_path, 'Unidentified_' + str(event) + '.xlsx')
        missing_age_file = os.path.join(storage_path, 'Missing_age_' + str(event) + '.xlsx')

        event_results = get_event(event, storage_path, apikey)
        if event in event_to_manual.keys():
            manual_df = event_to_manual[event]
        else:
            manual_df = pd.DataFrame()
        if not event_results.empty:  # Results exist in Eventor
            if sum(event_results.finished) > 0:  # At least one runner has finished the race
                event_points, unidentified, missing_age = add_points_to_event(event_results, manual=manual_df)
                event_points.to_csv(output_file, index=False)
                if not unidentified.empty:
                    print('Listar oidentifierade manuella löpare i ' + unidentified_file)
                    unidentified.to_excel(unidentified_file, index=False)
                if not missing_age.empty:
                    print('Listar okänd-ålder-löpare i ' + missing_age_file)
                    missing_age.to_excel(missing_age_file, index=False)


def evaluate_night(storage_path, event_list, apikey):
    for event in event_list:
        output_file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        unidentified_file = os.path.join(storage_path, 'Unidentified_' + str(event) + '.xlsx')
        missing_age_file = os.path.join(storage_path, 'Missing_age_' + str(event) + '.xlsx')

        event_results = get_event(event, storage_path,  apikey)
        if not event_results.empty:
            event_points, unidentified, missing_age = add_night_points_to_event(event_results)
            event_points.to_csv(output_file)
            if not unidentified.empty:
                unidentified.to_excel(unidentified_file, index=False)
            if not missing_age.empty:
                missing_age.to_excel(missing_age_file, index=False)


def get_resultlist(root, apikey, debugmode=False):
    # Get year of competition
    event_date_string = root.find('Event/FinishDate/Date')
    if event_date_string is None:
        print('Varning, okänt tävlingsdatum')
        event_year = np.nan
    else:
        date = datetime.strptime(event_date_string.text, '%Y-%m-%d')
        event_year = date.year
        event_date = event_date_string.text

    obj_event = root.find('Event/Name')
    if obj_event is None:
        print('Varning, okänt tävlingsnamn')
        event_name = '?'
    else:
        event_name = obj_event.text

    # Extract results from classes
    index = 0
    df = pd.DataFrame()
    for x in root.findall('ClassResult'):
        obj_eventclass = x.find('EventClass')
        class_name = obj_eventclass.find('Name').text
        if not included_class(class_name, debugmode):
            continue
        for y in x.findall('PersonResult'):  # Get result for each person
            index += 1
            obj_person = y.find('Person')
            if obj_person is not None:
                obj_given = obj_person.find('PersonName/Given')
                obj_last = obj_person.find('PersonName/Family')

                if (obj_given is not None) and (isinstance(obj_given.text, str)):
                    name = obj_given.text
                else:
                    name = '?'
                if (obj_last is not None) and (isinstance(obj_last.text, str)):
                    name = name + ' ' + obj_last.text
                else:
                    name = name + ' ' + '?'
                    print('Oväntat namn: ' + name)
            else:
                name = '?'
            obj_id = obj_person.find('PersonId')
            if obj_id is None:
                person_id = 0
            else:
                if obj_id.text is None:
                    person_id = 0
                else:
                    person_id = obj_id.text

            obj_birth = obj_person.find('BirthDate/Date')
            if obj_birth is None:
                birthyear = np.nan
            else:
                year_str = obj_birth.text[:4]
                if year_str.isdigit():
                    birthyear = int(year_str)
                else:
                    birthyear = np.nan

            obj_org = y.find('Organisation')
            if obj_org is None:
                orgid = int(0)
                club = 'Klubblös'
            else:
                obj_orgid = obj_org.find('OrganisationId')
                if obj_orgid is None:
                    orgid = int(0)
                    club = 'Klubblös'
                else:
                    orgid = int(obj_orgid.text)
                    obj_clubname= obj_org.find('Name')
                    if obj_clubname is None:
                        club = '?'
                        print(name)
                        print(club)
                    else:
                        club = obj_org.find('Name').text

            parent_org_id = get_parent_organisation(orgid, apikey)

            obj_res = y.find('Result/ResultPosition')
            if obj_res is None:
                position = 0
            else:
                str_position = obj_res.text
                if str_position.isdigit():
                    position = int(str_position)
                else:
                    print('Okänd position för ' + name)
                    position = 0

            obj_status = y.find('Result/CompetitorStatus')
            status = obj_status.get('value')
            if (status.lower() == 'didnotstart') | (status.lower() == 'cancelled'):
                started = False
            else:
                started = True

            if status.lower() == 'ok':
                finished = True
            else:
                finished = False

            seconds = 0
            if finished:
                obj_time=y.find('Result/Time')
                if not (obj_time is None):
                    time_string = obj_time.text
                    t = time_string.split(':')
                    if len(t) == 1:
                        seconds = int(t[0])
                    elif len(t) == 2:
                        seconds = int(t[0]) * 60 + int(t[1])
                    elif len(t) == 3:
                        seconds = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])

            df.at[index, 'event_year'] = int(event_year)
            df.at[index, 'event_date'] = event_date
            df.at[index, 'classname'] = class_name
            df.at[index, 'name'] = name
            df.at[index, 'personid'] = person_id
            df.at[index, 'birthyear'] = birthyear
            df.at[index, 'age'] = event_year - birthyear
            df.at[index, 'orgid'] = orgid
            df.at[index, 'club'] = club
            df.at[index, 'region'] = parent_org_id
            df.at[index, 'started'] = started
            df.at[index, 'finished'] = finished
            df.at[index, 'position'] = position
            df.at[index, 'seconds'] = seconds

    if not df.empty:
        integer_columns = ['event_year', 'personid', 'position', 'region', 'orgid', 'seconds']
        for col in integer_columns:
            if all(~df[col].isna()):
                df = df.assign(**{col: df[col].astype('int')})
    return df


def get_parent_organisation(id, apikey):

    parent_org = get_parent_org_quick(id)
    if not (parent_org is None):
        return parent_org
    else:
        # Fetch organisation id from Eventor
        headers = {'ApiKey': apikey}

        if not isinstance(id, str):
            id = str(id)

        response = requests.get('https://eventor.orientering.se/api/organisation/' + id, headers=headers)
        root = ET.fromstringlist(response.text)
        obj_parent = root.find('ParentOrganisation/OrganisationId')
        if obj_parent is None:
            parent_org = 0
        else:
            parent_org = int(obj_parent.text)

        return parent_org


def get_region_table(apikey):
    headers = {'ApiKey': apikey}

    url = "https://eventor.orientering.se/api/organisation"
    response = requests.get(url, headers=headers)

    root = ET.fromstringlist(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.prettify()

    return root, response


def concatenate(storage_path, event_list):
    df = pd.DataFrame()
    for event in event_list:
        file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        if os.path.exists(file):
            df0 = pd.read_csv(file, index_col=False)
            if 'Unnamed: 0' in df0.columns:
                df0 = df0.drop(columns=['Unnamed: 0'])
            df0 = df0.assign(eventid=event)
            if df.empty:
                df = df0.copy()
            else:
                df = df.append(df0, sort=False, ignore_index=True)
    df = df.reset_index(drop=True, inplace=False)
    return df


def get_user_events(user_input, value='event_ids', apikey=''):
    event_ids = []
    event_names = []
    if value in user_input.keys():
        if isinstance(user_input[value], float) | isinstance(user_input[value], int):
            event_ids = [int(user_input[value])]
        else:
            if ',' in user_input[value]:
                event_strings = user_input[value].split(',')
                for id in event_strings:
                    id = id.replace(' ', '')
                    if id.isdigit():
                        event_ids.append(int(id))
            else:
                if user_input[value].isdigit():
                    event_ids = [int(user_input[value])]

        for race in event_ids:
            if apikey is None:  # Debug-mode
                event_names.append(str(race))
            else:
                name, year = get_event_name(race, apikey)
                event_names.append(name + ' (' + str(year) + ')')

    return event_ids, event_names


def print_event_names(day_events, night_events):
    print(' ')
    if len(day_events)>1:
        print('Listade ordinarie tävlingar (dag):')
    else:
        print('Listad tävling (dag):')
    for event in day_events:
        print(event)
    print(' ')
    if night_events:
        if len(day_events) > 1:
            print('Listade natt-tävlingar:')
        else:
            print('Listad natt-tävling:')
        for event in night_events:
            print(event)
    print(' ')


def extract_and_analyse(storage_path, race_to_manual_info, club_division_df, user_input, apikey=None):
    if 'event_ids' not in user_input.keys():
        raise ValueError('event_ids is missing in user_input dataframe')

    event_ids, day_names = get_user_events(user_input, 'event_ids', apikey)
    night_ids, night_names = get_user_events(user_input, 'night_ids', apikey)
    print_event_names(day_names, night_names)

    get_events(storage_path, event_ids, apikey)
    evaluate(storage_path, event_ids, apikey, race_to_manual_info)

    get_events(storage_path, night_ids, apikey)
    evaluate_night(storage_path, night_ids, apikey)
    df_night = concatenate(storage_path, night_ids)

    df = concatenate(storage_path, event_ids)

    if 'night' in race_to_manual_info.keys():
        df_night = add_manual_night_runners(race_to_manual_info['night'], df_night)

    cleaned_division_df = clean_division_input(club_division_df)

    df_club_summary, club_results = club_summary(df, cleaned_division_df)
    df_club_summary = sort_based_on_division(df_club_summary)
    club_file = club_results_to_excel(storage_path, df_club_summary, club_results)

    si = individual_summary(df, df_night)
    indiv_file = individual_results_excel(storage_path, si)
    return club_file, indiv_file


if __name__ == "__main__":
    manual, club_division, user_dct = read_manual_input(manual_input_file='C:\\Users\\Klas\\Desktop\\Example_inputs\\Manual_input_2022.xlsx')
    extract_and_analyse(storage_path='C:\\Users\\Klas\\Desktop\\results_2022', race_to_manual_info=manual,
                        club_division_df=club_division, user_input=user_dct)
