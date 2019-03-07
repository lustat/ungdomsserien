from loader.read_results import extract_and_analyse, get_events, get_event
import os

print('Test file: ')

event_ids = [20550, 21406, 21376, 21988, 21732, 21644]
night_ids = [21851, 21961]

#key = input('Input api key: ')
key = os.environ["apikey"]
storage_path = 'C:\\Users\\Klas\\PycharmProjects\\output'

club_file, ind_file = extract_and_analyse(storage_path, event_ids, night_ids, key)

input('Press Enter to exit')
