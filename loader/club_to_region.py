import yaml
import requests
from xml.etree import ElementTree

from definitions import DATA_DIR


def fetch_organisation_from_eventor(club_id, apikey=None):
    headers = {'ApiKey': apikey}

    if not isinstance(club_id, str):
        club_id = str(club_id)

    response = requests.get(f'https://eventor.orientering.se/api/organisation/{club_id}', headers=headers)
    root = ElementTree.fromstringlist(response.text)
    obj_parent = root.find('ParentOrganisation/OrganisationId')
    if obj_parent is None:
        parent_org = 0
    else:
        parent_org = int(obj_parent.text)

    return parent_org


def read_yaml_file(file_name='club_to_region.yaml'):
    with open(f'{DATA_DIR}/02_raw_data/{file_name}', 'r') as file:
        dct = yaml.safe_load(file)
    return dct


def get_parent_organisation(club_id, apikey=None):
    club_to_organisation = read_yaml_file()
    if club_id in club_to_organisation.keys():
        return club_to_organisation[club_id]
    else:  # Club is missing. Update yaml data
        if not apikey:
            raise ValueError(f'An eventor call is needed and the apikey is missing')
        organisation_id = fetch_organisation_from_eventor(club_id, apikey)
        club_to_organisation[club_id] = organisation_id
        with open(f"{DATA_DIR}/02_raw_data/club_to_region.yaml", "w") as file:
            print(f'Updating yaml-file: {club_id}: {organisation_id}')
            yaml.dump(club_to_organisation, file)
        return organisation_id


if __name__ == '__main__':
    club_number = 1586
    print(get_parent_organisation(club_number))
