import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from loader.loader_utils import rel2fullpath
from calculation.points_calculation import add_points_to_event_result


def xmlstring2file(response, xmlname):
    # soup = BeautifulSoup(response.text, 'html.parser')
    # text = soup.prettify()
    if xmlname:
        xmlfile = os.path.join(rel2fullpath('data'), xmlname)
        with open(xmlfile, "w") as text_file:
            print(response.text, file=text_file)


def get_event(event_id):
    storage_path = rel2fullpath('events_storage')
    output_file = os.path.join(storage_path, str(event_id) + '.parq')

    if not os.path.exists(output_file):  #Load events
        url = "https://eventor.orientering.se/api/results/event"
        apikey = os.environ["apikey"]
        headers = {'ApiKey': apikey}
        response = requests.get(url, headers=headers, params={'eventId': event_id, 'includeSplitTimes': False})
        root = ET.fromstringlist(response.text)
        df = get_resultlist(root)
        print('Storing ' + output_file)
        df.to_parquet(output_file)

    else:  # Load already stored event
        df = pd.read_parquet(output_file)


    return df


def get_resultlist(root):
    index = 0
    df = pd.DataFrame()
    for x in root.findall('ClassResult'):  # Read every class
        obj_eventclass = x.find('EventClass')
        class_name = obj_eventclass.find('Name').text
        print(class_name)
        for y in x.findall('PersonResult'):  # Get result for each person
            index += 1
            obj_person = y.find('Person')
            name = obj_person.find('PersonName/Given').text + ' ' + obj_person.find('PersonName/Family').text

            person_id = obj_person.find('PersonId').text
            obj_birth = obj_person.find('BirthDate/Date')
            if obj_birth is None:
                birthyear = np.nan
            else:
                birthyear = obj_birth.text[:4]

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

            parent_org_id = get_parent_organisation(orgid)

            obj_res = y.find('Result/ResultPosition')
            if obj_res is None:
                position = 'x'
            else:
                position = obj_res.text

            finishtime = y.find('Result/FinishTime/Clock')
            if obj_res is None:
                finished = False
            else:
                finished = True

            df.at[index, 'classname'] = class_name
            df.at[index, 'name'] = name
            df.at[index, 'personid'] = person_id
            df.at[index, 'birthyear'] = birthyear
            df.at[index, 'orgid'] = orgid
            df.at[index, 'club'] = club
            df.at[index, 'region'] = parent_org_id
            df.at[index, 'started'] = started
            df.at[index, 'finished'] = finished
            df.at[index, 'position'] = position

    return df


def get_parent_organisation(id='16'):
    if not isinstance(id, str):
        id = str(id)

    response = requests.get('https://eventor.orientering.se/api/organisation/' + id, headers=headers)
    root = ET.fromstringlist(response.text)
    obj_parent = root.find('ParentOrganisation/OrganisationId')
    if obj_parent == None:
        parent_org = 0
    else:
        parent_org = int(obj_parent.text)

    return parent_org


def get_region_table():
    apikey = os.environ["apikey"]
    headers = {'ApiKey': apikey}

    url = "https://eventor.orientering.se/api/organisation"
    response = requests.get(url, headers=headers)

    root = ET.fromstringlist(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.prettify()

    return root, response

if __name__ == "__main__":
    apikey = os.environ["apikey"]
    headers = {'ApiKey': apikey}

    eventid = 18218
    event_results = get_event(eventid)
    results_with_points = add_points_to_event_result(event_results)

    print(results_with_points)
    print('Finished')
