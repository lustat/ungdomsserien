import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd

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
from definitions import OUTPUT_DIR, NOT_STARTED_NAMES, TOTAL_COMPETITIONS


def get_events(storage_path, event_list, apikey=None):
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    for event in event_list:
        get_event(event, storage_path, apikey)


def get_event(event_id, storage_path, apikey=None, debugmode=False, additional_excel=False):
    if apikey is None:
        apikey = os.environ["apikey"]

    output_file = f'{storage_path}/{event_id}.parquet'
    if not os.path.exists(output_file):  # Load event
        url = "https://eventor.orientering.se/api/results/event"
        headers = {'ApiKey': apikey}
        response = requests.get(url, headers=headers, params={'eventId': event_id, 'includeSplitTimes': False})
        root = ET.fromstringlist(response.text)
        df = get_resultlist(root, apikey, debugmode)
        if not df.empty:
            if sum(df.finished) > 0:
                print('Sparar resultat: ' + output_file)
                df.to_parquet(output_file, index=False)
                if additional_excel:
                    output_excel = output_file.replace('.parquet', '.xlsx')
                    df.to_excel(output_excel)
            else:
                df = pd.DataFrame()
    else:  # Load already stored event
        print('Läser in lokal fil: ' + str(output_file))
        df = pd.read_parquet(output_file)
        # output_excel = output_file.replace('.parquet', '.xlsx')
        # df.to_excel(output_excel)
    return df


def evaluate(storage_path, event_list, apikey, event_to_manual):

    for event in event_list:
        output_file = f'{storage_path}/result_{event}.parquet'
        unidentified_file = f'{storage_path}/Unidentified_{event}.xlsx'
        missing_age_file = f'{storage_path}/Missing_age_{event}.xlsx'

        event_results = get_event(event, storage_path, apikey)
        if event in event_to_manual.keys():
            manual_df = event_to_manual[event]
        else:
            manual_df = pd.DataFrame()
        if not event_results.empty:  # Results exist in Eventor
            if sum(event_results.finished) > 0:  # At least one runner has finished the race
                event_points, unidentified, missing_age = add_points_to_event(event_results, manual=manual_df)
                event_points.to_parquet(output_file)
                if not unidentified.empty:
                    print('Listar oidentifierade manuella löpare i ' + unidentified_file)
                    unidentified.to_excel(unidentified_file, index=False)
                if not missing_age.empty:
                    print('Listar okänd-ålder-löpare i ' + missing_age_file)
                    missing_age = missing_age.assign(**{'include (Y/N/?)': '?'})
                    missing_age.to_excel(missing_age_file, index=False)


def evaluate_night(storage_path, event_list, apikey):
    for event in event_list:
        output_file = f'{storage_path}/result_{event}.parquet'
        unidentified_file = f'{storage_path}/Unidentified_{event}.xlsx'
        missing_age_file = f'{storage_path}/Missing_age_{event}.xlsx'

        event_results = get_event(event, storage_path,  apikey)
        if not event_results.empty:
            event_points, unidentified, missing_age = add_night_points_to_event(event_results)
            event_points.to_parquet(output_file)
            if not unidentified.empty:
                unidentified.to_excel(unidentified_file, index=False)
            if not missing_age.empty:
                missing_age.to_excel(missing_age_file, index=False)


def get_field(object, field_name, default, dtype=None):
    if object is None:
        return default

    value = object.findtext(field_name)
    if (value is None) | (value == ''):
        value = default

    if dtype is not None:
        value = dtype(value)

    return value


def get_resultlist(root, apikey, debugmode=False):
    # Get year of competition
    event_date_string = root.find('Event/FinishDate/Date')
    if event_date_string is None:
        print('Varning, okänt tävlingsdatum')
        event_year = np.nan
        event_date = '?'
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

    obj_event = root.find('Event/EventId')
    if obj_event is None:
        print('Varning, okänt tävlings-ID')
        event_id = 0
    else:
        event_id = int(obj_event.text)

    print(f'Hämtar: {event_name} (https://eventor.orientering.se/Events/Show/{event_id})')

    # Extract results from classes
    df = pd.DataFrame()
    for x in root.findall('ClassResult'):
        class_name = x.findtext('EventClass/Name')
        if not included_class(class_name, debugmode):
            continue

        for y in x.findall('PersonResult'):  # Get result for each person
            person = y.find('Person')

            name = f"{get_field(person, 'PersonName/Given', '')} {get_field(person, 'PersonName/Family', '?')}"
            person_id = get_field(person, 'PersonId', '0', np.int64)
            birth_date = get_field(person, 'BirthDate/Date', '', str)
            birth_year = int(birth_date[:4]) if birth_date != '' else np.nan

            org = y.find('Organisation')
            orgid = get_field(org, 'OrganisationId', 0, int)
            club = get_field(org, 'Name', 'Klubblös', str)
            parent_org_id = get_parent_organisation(orgid, apikey)

            position = get_field(y, 'Result/ResultPosition', 0, int)
            status_raw = y.find('Result/CompetitorStatus')
            status = status_raw.get('value').lower() if status_raw is not None else ''
            started = status not in NOT_STARTED_NAMES
            finished = status == 'ok'

            seconds = 0
            if finished:
                obj_time = y.find('Result/Time')
                if not (obj_time is None):
                    time_string = obj_time.text
                    t = time_string.split(':')
                    if len(t) == 1:
                        seconds = int(t[0])
                    elif len(t) == 2:
                        seconds = int(t[0]) * 60 + int(t[1])
                    elif len(t) == 3:
                        seconds = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])

            idx = len(df)
            df.at[idx, 'event_year'] = int(event_year)
            df.at[idx, 'event_date'] = event_date
            df.at[idx, 'classname'] = class_name
            df.at[idx, 'name'] = name
            df.at[idx, 'personid'] = person_id
            df.at[idx, 'birthyear'] = birth_year
            df.at[idx, 'age'] = event_year - birth_year
            df.at[idx, 'orgid'] = orgid
            df.at[idx, 'club'] = club
            df.at[idx, 'region'] = parent_org_id
            df.at[idx, 'started'] = started
            df.at[idx, 'finished'] = finished
            df.at[idx, 'position'] = position
            df.at[idx, 'seconds'] = seconds
            df.at[idx, 'eventid'] = event_id

    if not df.empty:
        integer_columns = ['event_year', 'personid', 'position', 'region', 'orgid',
                           'seconds', 'birthyear', 'age', 'eventid']
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

        # Lägg till följande rad i get_parent_org_quick:
        print(f'        {id}: {parent_org},')

        return parent_org


def get_region_table(apikey):
    headers = {'ApiKey': apikey}

    url = "https://eventor.orientering.se/api/organisation"
    response = requests.get(url, headers=headers)

    root = ET.fromstringlist(response.text)
    return root, response


def concatenate(storage_path, event_list):
    dfs = []
    for event in event_list:
        file = f'{storage_path}/result_{event}.parquet'
        if os.path.exists(file):
            print(f'Läser parquet file: {file}')
            df0 = pd.read_parquet(file)
            if not df0.empty:
                dfs.append(df0)
    df = pd.concat(dfs, sort=False, ignore_index=True)
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
    if len(day_events) > 1:
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

    if df.event_date.nunique() == TOTAL_COMPETITIONS:
        # Lägg till fil för utlottning vid Älgot Cup
        lottery = pd.DataFrame(df.personid.value_counts()).reset_index(drop=False)
        lottery = lottery.loc[(lottery.personid >= 3) & (lottery.index != 0)]
        lottery = lottery.rename(columns={'personid': 'events'})
        lottery = lottery.rename(columns={'index': 'personid'})
        df0 = df[['personid', 'name', 'club']]
        df0 = df0.loc[df0.personid.isin(lottery.personid)]
        df0 = df0.drop_duplicates('personid')[['name', 'club']]
        lottery_file = f'{OUTPUT_DIR}/lottery.xlsx'
        df0.to_excel(lottery_file, index=False)
        print('Skapade lotterilista: ' + lottery_file)

    df_club_summary, club_results = club_summary(df, cleaned_division_df)
    df_club_summary = sort_based_on_division(df_club_summary)
    club_file = club_results_to_excel(storage_path, df_club_summary, club_results)

    si = individual_summary(df, df_night)
    indiv_file = individual_results_excel(storage_path, si)
    return club_file, indiv_file


if __name__ == "__main__":
    manual, club_division, user_dct = read_manual_input(manual_input_file='C:/PycharmProjects/ungdomsserien/input/Manual_input_2024.xlsx')
    extract_and_analyse(storage_path='C:/PycharmProjects/ungdomsserien/output/results_2024', race_to_manual_info=manual,
                        club_division_df=club_division, user_input=user_dct)
