import pandas as pd
import numpy as np
from definitions import EVENT_COUNT

def individual_summary(df, df_night, class_selection=None, event_column='event_date'):
    if not df_night.empty:
        df_night = df_night.assign(found=False)

    if df.empty:
        return {}

    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    if event_column == 'event_date':
        event_dates = list(df[event_column].unique())
        event_ids = list(df.eventid.unique())
        if len(event_dates) < len(event_ids):
            event_column = 'eventid'

    summary = {}
    for classname in class_selection:
        print('Individuell summering för ' + classname)
        df_class = df.loc[df.classname == classname]
        ids = [pid for pid in df_class.personid.unique() if not (pid is None)]
        events = list(df_class[event_column].unique())

        columns = ['name', 'club']
        columns.extend(events)
        columns.extend(['score', 'night', 'total'])
        class_summary = pd.DataFrame(index=ids, columns=columns)
        for pid in ids:
            res_person = df_class.loc[df_class.personid == pid]
            if np.isnan(pid):
                print(' -----  ')
                print(pid)
                print(res_person.name)
            class_summary.at[pid, 'name'] = res_person.name.iloc[0]
            class_summary.at[pid, 'club'] = res_person.club.iloc[0]
        for event in events:
            df_race = df_class.loc[df_class[event_column] == event]

            for pid in ids:
                res_person = df_race.loc[df_race.personid == pid]
                if df_night.empty:
                    night_person = pd.DataFrame()
                else:
                    night_person = df_night.loc[df_night.personid == pid]

                if len(res_person) == 1:
                    class_summary.at[pid, event] = res_person.points.iloc[0]
                else:
                    class_summary.at[pid, event] = 0

                if night_person.empty | (classname in ['D10', 'H10']):
                    class_summary.at[pid, 'night'] = 0
                else:
                    class_summary.at[pid, 'night'] = max(night_person.points)
                    for index in night_person.index:
                        df_night.at[index, 'found'] = True

        class_summary = total_score_for_best_n_events(class_summary, events)
        class_summary = class_summary.assign(total=class_summary.score + class_summary.night)
        class_summary = class_summary.sort_values(by='total', inplace=False, ascending=False)

        class_summary = add_final_position(class_summary)
        summary[classname] = class_summary

    #df_only_night = df_night[(~df_night.found) & (~(df_night.classname=='H10')) & (~(df_night.classname=='D10'))]
    return summary


def total_score_for_best_n_events(df, events, n=EVENT_COUNT):
    points = df[events].values
    sorted_points = -np.sort(-points, axis=1)  #Sort in descending order

    # Sum over n best competitions
    np.sum(sorted_points[:, :n])
    score = np.sum(sorted_points[:, :n], axis=1)
    df = df.assign(score=score)
    return df


def club_summary(df, division_df, event_column='event_date'):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = df.loc[~df.orgid.isna()]
    df = df.assign(orgid=df.orgid.astype(int))

    if event_column == 'event_date':
        event_dates = list(df[event_column].unique())
        event_ids = list(df.eventid.unique())
        if len(event_dates) != len(event_ids):
            event_column = 'eventid'

    events = list(df[event_column].unique())
    organisations = list(df.orgid.unique())

    summary = pd.DataFrame(index=organisations)
    for orgid in organisations:
        df0 = df.loc[df.orgid == orgid]
        summary.at[orgid, 'club'] = df0.club.iloc[0]

    for event in events:
        summary = summary.assign(**{str(event): 0})
        df_event = df.loc[df[event_column] == event]
        x = df_event.groupby(by='orgid')
        summed_points = x.points.sum()
        summary = summary.assign(**{str(event): summed_points})
        na_rows = summary.loc[summary[str(event)].isna().values].index
        for key in na_rows:
            summary.at[key, str(event)] = 0
        summary = summary.assign(**{str(event): summary[str(event)].astype(int)})

    events_str = [str(event) for event in events]
    summary = total_score_for_best_n_events(summary, events_str)
    summary = summary.sort_values(by='score', ascending=False, inplace=False)

    clublist = club_points_per_event(df, summary.index)

    if division_df.empty:
        summary = summary.assign(division=np.nan)
    else:
        if 'orgid' in division_df.columns:
            division_df = division_df.set_index('orgid', drop=True)
            summary = summary.join(division_df, how='left', lsuffix='', rsuffix='_division')
            summary.loc[summary.division.isna(), 'division'] = 'Okänd division'
            if 'club_division' in summary.columns:
                mismatch = summary.loc[summary.club != summary.club_division]
                if not mismatch.empty:
                    print(' ')
                    print('Klubbnamn i divisionstabell matchar ej')
                    print('Dubbelkolla Excel-fil')
                    for (key, row) in mismatch.iterrows():
                        print(str(row.club) + '  =?   ' + str(row.club_division))
                    print(' ')
                summary = summary.drop(columns=['club_division'])
        else:
            raise ValueError('orgid missing in data frame')

    return summary, clublist


def club_points_per_event(df, club_ids=None):
    """List all points per event for each club

    :return: List of dataframes, where each dataframe correspond to a club
    """
    if club_ids is None:
        club_ids=df.orgid.unique()

    lst = []
    for clubid in club_ids:
        df_club = df.loc[df.orgid == clubid]
        lst.append(df_club)

    return lst


def add_final_position(df):
    df = df.assign(position=0)
    for (key, row) in df.iterrows():
        df.at[key, 'position'] = sum(df.total > row.total) + 1

    return df


def sort_based_on_division(summary):
    if summary.empty:
        return summary
    if 'division' not in summary.columns:
        return summary
    if all(summary.division.isna()):
        return summary

    for (key, row) in summary.iterrows():
        if not isinstance(row.division, str):
            summary.at[key, 'division'] = 'Okänd division'
        else:
            # Make sure division value starts with capital letter
            summary.at[key, 'division'] = row.division.capitalize()

    dct = {'Elit': 0}
    summary = summary.assign(division_number=-1)
    for (key, row) in summary.iterrows():
        if row.division in dct.keys():
            summary.at[key, 'division_number'] = dct[row.division]
        else:
            if row.division.startswith('Division '):
                number = row.division.replace('Division ', '')
                if number.isdigit():
                    summary.at[key, 'division_number'] = int(number)

    # Set unknown divisions to "max+1" division
    number_for_unknown = summary.division_number.max() + 1
    summary.loc[summary.division_number == -1, 'division_number'] = number_for_unknown

    sorted_summary = pd.DataFrame()
    for number in summary.division_number.unique():
        df_temp = summary.loc[summary.division_number==number]
        df_temp = df_temp.sort_values(by='score', ascending=False)
        sorted_summary = sorted_summary.append(df_temp)

    sorted_summary = sorted_summary.drop(columns=['division_number'])
    return sorted_summary
