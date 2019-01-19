from loader.read_results import extract_and_analyse, get_events, get_event
from base_utils import rel2fullpath


print('Test file: ')

eventlist = [18218, 17412, 18308, 18106, 16981, 18995]
nightlist = [18459, 18485]

key = input('Input api key: ')

club_file, ind_file = extract_and_analyse(eventlist, nightlist, key)
#get_event(eventlist[0], key)

# storage_path = rel2fullpath('events_storage')
# print(storage_path)

input('Press Enter to exit')
