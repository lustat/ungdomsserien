from loader.read_results import extract_and_analyse, get_events, get_event


print('Test file: ')

eventlist = [18218, 17412, 18308, 18106, 16981, 18995]
nightlist = [18459, 18485]
key = input('Input api key: ')
storage_path = 'C:\\Users\\Klas\\PycharmProjects\\output'

club_file, ind_file = extract_and_analyse(storage_path, eventlist, nightlist, key)

input('Press Enter to exit')
