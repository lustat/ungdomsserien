import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np


def xmlstring2file(response, xmlname):
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.prettify()


def get_event(event_id):
    url = "https://eventor.orientering.se/api/results/event"
    apikey = os.environ["apikey"]
    headers = {'ApiKey': apikey}

    response = requests.get(url, headers=headers, params={'eventId': eventid, 'includeSplitTimes': False})

    root = ET.fromstringlist(response.text)
    return root, response


def get_resultlist(root):
    index = 0
    df = pd.DataFrame()
    for x in root.findall('ClassResult'):
        print(x.attrib)
        obj_eventclass = x.find('EventClass')
        eventname = obj_eventclass.find('Name').text
        print()
        for y in x.findall('PersonResult'):
            index += 1
            obj_person = y.find('Person')
            name = obj_person.find('PersonName/Given').text +' ' + obj_person.find('PersonName/Family').text
            position = obj_person.find('PersonName/Given').text

            person_id = obj_person.find('PersonId').text
            obj_birth = obj_person.find('BirthDate/Date')
            if obj_birth == None:
                birthyear = np.nan
            else:
                birthyear = obj_birth.text[:4]


            obj_org = y.find('Organisation')
            if obj_org == None:
                orgid = int(0)
                club = 'Klubblös'
            else:
                orgid = int(obj_org.find('OrganisationId').text)
                club = obj_org.find('Name').text

            obj_res = y.find('Result/ResultPosition')
            if obj_res == None:
                position = 'x'
            else:
                position = obj_res.text

            df.at[index, 'eventname'] = eventname
            df.at[index, 'name'] = name
            df.at[index, 'personid'] = person_id
            df.at[index, 'birthyear'] = birthyear
            df.at[index, 'orgid'] = orgid
            df.at[index, 'club'] = club
            df.at[index, 'position'] = position

    return df


if __name__ == "__main__":
    # eventid = 18667
    eventid = 23906
    xmlroot, resp = get_event(eventid)
    reslist = get_resultlist(xmlroot)
    print(reslist)
    print('Finished')
