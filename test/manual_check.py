from loader.read_results import get_events, concatenate, get_event
if __name__ == "__main__":
    event_ids = [18218, 17412, 18308, 18106, 16981, 18995]
    get_events(event_ids)
    df = concatenate(event_ids)
    club_result = df.loc[df.club == 'Lunds OK']
    x = club_result.loc[club_result.eventid==16981].sort_values(by='name')[['name','points']]
    print(x)

    df = get_event(16981)
    for cname in ['Öppen motion 1', 'Öppen motion 3', 'Öppen motion 5']:
        om = df.loc[df.classname == cname]
        club_om = om.loc[om.club == 'Lunds OK']
        print(club_om[['name', 'age']])
    print('Finished')
