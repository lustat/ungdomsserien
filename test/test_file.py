from loader.read_results import extract_and_analyse

print('Test file: ')

eventlist = [18218, 17412, 18308, 18106, 16981, 18995]
nightlist = [18459, 18485]

club_file, ind_file = extract_and_analyse(eventlist, nightlist)
input('Press any button to exit')
