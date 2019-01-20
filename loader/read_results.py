import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from loader.loader_utils import included_class
from base_utils import rel2fullpath
from calculation.points_calculation import add_points_to_event, add_night_points_to_event
from calculation.summarize import individual_summary, club_summary
from datetime import datetime
from output.create_excel import individual_results_excel, club_results_excel
import time


def get_events(event_list, apikey):
    for event in event_list:
        get_event(event, apikey)


def xmlstring2file(response, xmlname):
    # soup = BeautifulSoup(response.text, 'html.parser')
    # text = soup.prettify()
    if xmlname:
        xmlfile = os.path.join(rel2fullpath('data'), xmlname)
        with open(xmlfile, "w") as text_file:
            print(response.text, file=text_file)


def get_event(event_id, apikey=None, debugmode=False):
    if apikey is None:
        apikey = os.environ["apikey"]

    storage_path = rel2fullpath('events_storage')
    output_file = os.path.join(storage_path, str(event_id) + '.csv')
    if not os.path.exists(output_file):  #Load events
        url = "https://eventor.orientering.se/api/results/event"

        headers = {'ApiKey': apikey}
        response = requests.get(url, headers=headers, params={'eventId': event_id, 'includeSplitTimes': False})
        root = ET.fromstringlist(response.text)
        df = get_resultlist(root, apikey, debugmode)
        print('Storing ' + output_file)
        df.to_csv(output_file)
    else:  # Load already stored event
        print('Reloading an already stored event: ' + output_file)

    df = pd.read_csv(output_file)
    return df


def evaluate(event_list, apikey):
    storage_path = rel2fullpath('events_storage')
    print(storage_path)

    for event in event_list:
        output_file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        if not os.path.exists(output_file):
            event_results = get_event(event, apikey)
            event_points = add_points_to_event(event_results)
            print('Storing ' + output_file)
            event_points.to_csv(output_file)


def evaluate_night(event_list, apikey):
    storage_path = rel2fullpath('events_storage')

    for event in event_list:
        output_file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        if not os.path.exists(output_file):
            event_results = get_event(event, apikey)
            event_points = add_night_points_to_event(event_results)
            print('Storing ' + output_file)
            event_points.to_csv(output_file)


def get_resultlist(root, apikey,debugmode=False):
    # Get year of competition
    event_date = root.find('Event/FinishDate/Date')
    if event_date is None:
        print('Warning, unknown competition date')
        event_year = np.nan
    else:
        date = datetime.strptime(event_date.text, '%Y-%m-%d')
        event_year = date.year

    obj_event = root.find('Event/Name')
    if obj_event is None:
        print('Warning, unknown competition name')
        event_name = '?'
    else:
        event_name = obj_event.text
    print(event_name)

    # Extract results from classes
    index = 0
    df = pd.DataFrame()
    for x in root.findall('ClassResult'):
        obj_eventclass = x.find('EventClass')
        class_name = obj_eventclass.find('Name').text
        if not included_class(class_name, debugmode):
            print('Skip ' + class_name)
            continue
        print('Loading ' + class_name)
        time.sleep(1)
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
                    print('Unexpected name: ' + name)
            else:
                name = '?'
            obj_id = obj_person.find('PersonId')
            if obj_id is None:
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
                    print('Unknown position for ' + name)
                    position = 0

            obj_status = y.find('Result/CompetitorStatus')
            status = obj_status.get('value')
            if status.lower() == 'didnotstart':
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
                    t=time_string.split(':')
                    if len(t) == 1:
                        seconds = int(t[0])
                    elif len(t) == 2:
                        seconds = int(t[0]) * 60 + int(t[1])
                    elif len(t) == 3:
                        seconds = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])

            df.at[index, 'event_year'] = int(event_year)
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

    numerical_columns=['event_year', 'personid', 'birthyear', 'position', 'region', 'orgid', 'seconds']
    for col in numerical_columns:
        if all(~df[col].isna()):
            print(col)
            df = df.assign(**{col: df[col].astype('int')})
    return df


def get_parent_organisation(id, apikey):
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
    # apikey = os.environ["apikey"]
    headers = {'ApiKey': apikey}

    url = "https://eventor.orientering.se/api/organisation"
    response = requests.get(url, headers=headers)

    root = ET.fromstringlist(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.prettify()

    return root, response


def concatenate(event_list):
    storage_path = rel2fullpath('events_storage')

    df = pd.DataFrame()
    for event in event_list:
        file = os.path.join(storage_path, 'Result_' + str(event) + '.csv')
        df0 = pd.read_csv(file)
        df0 = df0.assign(eventid=event)
        if df.empty:
            df = df0.copy()
        else:
            df = df.append(df0, sort=False)

    return df


def extract_and_analyse(event_ids=None, night_ids=None, apikey=None):
    if event_ids is None:
        event_ids = [18218, 17412, 18308, 18106, 16981, 18995]
    if night_ids is None:
        night_ids = [18459, 18485]

    get_events(event_ids, apikey)
    evaluate(event_ids, apikey)

    get_events(night_ids, apikey)
    evaluate_night(night_ids, apikey)
    df_night = concatenate(night_ids)

    df = concatenate(event_ids)

    df_club_summary, club_results = club_summary(df)
    club_file = club_results_excel(df_club_summary, club_results)

    si = individual_summary(df, df_night)
    indiv_file = individual_results_excel(si)
    return club_file, indiv_file

if __name__ == "__main__":
    print('Extract and evaluate orienteering events')
    extract_and_analyse()
    print('Finished')

