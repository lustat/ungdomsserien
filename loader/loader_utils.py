import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def get_event_name(id, apikey=None):
    if apikey is None:
        apikey = os.environ["apikey"]

    headers = {'ApiKey': apikey}

    if not isinstance(id, str):
        id = str(id)

    response = requests.get('https://eventor.orientering.se/api/event/' + id, headers=headers)
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


def included_class(class_name, debugmode=False):
    class_name = class_name.replace(' ', '')
    if debugmode:
        if class_name.lower().startswith('sv'):
            output = True
        else:
            output = False
        return output

    if (not isinstance(class_name, str)) or (class_name == ''):
        return False

    output = False
    if (class_name.lower().startswith('h')) or (class_name.lower().startswith('d')):
        if len(class_name) == 3:
            class_year = class_name[1:]
            if class_year.isdigit():
                class_year = int(class_year)
                if class_year <= 16:
                    output = True

        if class_name.lower().endswith('kort') | class_name.lower().endswith('k'):
            class_name = class_name.replace('Kort', '')
            class_name = class_name.replace('kort', '')
            class_name = class_name.replace('k', '')
            if len(class_name) == 3:
                class_year = class_name[1:]
                if class_year.isdigit():
                    class_year = int(class_year)
                    if class_year <= 16:
                        output = True
    else:
        # All other classes are assumed to be open
        output = True

    return output
