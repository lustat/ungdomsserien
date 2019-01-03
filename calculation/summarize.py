import pandas as pd
import numpy as np


def individual_summary(df, df_night, class_selection=None):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    summary = {}
    for classname in class_selection:
        df_class = df.loc[df.classname == classname]
        ids = [pid for pid in df_class.personid.unique() if not (pid is None)]
        events = list(df_class.eventid.unique())
        # str_events = [str(event) for event in events]

        columns = ['name', 'club']
        columns.extend(events)
        columns.extend(['score','night','total'])
        class_summary = pd.DataFrame(index=ids, columns=columns)
        for pid in ids:
            res_person = df_class.loc[df_class.personid == pid]
            class_summary.at[pid, 'name'] = res_person.name.iloc[0]
            class_summary.at[pid, 'club'] = res_person.club.iloc[0]
        for event in events:
            df_race = df_class.loc[df_class.eventid == event]

            for pid in ids:
                res_person = df_race.loc[df_race.personid == pid]
                night_person = df_night.loc[df_night.personid == pid]
                if len(res_person)==1:
                    class_summary.at[pid, event] = res_person.points.iloc[0]
                else:
                    class_summary.at[pid, event] = 0

                if night_person.empty | (classname in ['D10', 'H10']):
                    class_summary.at[pid, 'night'] = 0
                else:
                    class_summary.at[pid, 'night'] = max(night_person.points)
                    
        class_summary = add_best4_score(class_summary, events)
        class_summary = class_summary.assign(total=class_summary.score + class_summary.night)
        summary[classname] = class_summary
    return summary


def add_best4_score(df, events):
    points = df[events].values
    sorted_points =  -np.sort(-points, axis=1)  #Sort in descending order

    # Sum over four best competitions
    np.sum(sorted_points[:,:4])
    score = np.sum(sorted_points[:,:4],axis=1)
    df = df.assign(score = score)
    df = df.sort_values(by='score', inplace=False, axis=0)
    df = df.sort_values(by='score', inplace=False, ascending=False)
    return df


def club_summary(df):
    df = df.loc[~df.orgid.isna()]
    df = df.assign(orgid=df.orgid.astype(int))

    events = list(df.eventid.unique())
    organisations = list(df.orgid.unique())

    summary = pd.DataFrame(index=organisations)
    for orgid in organisations:
        df0 = df.loc[df.orgid == orgid]
        summary.at[orgid, 'club'] = df0.club.iloc[0]

    for event in events:
        summary = summary.assign(**{str(event): 0})
        df_event = df.loc[df.eventid==event]
        x = df_event.groupby(by='orgid')
        summed_points = x.points.sum()
        summary = summary.assign(**{str(event): summed_points})
        na_rows = summary.loc[summary[str(event)].isna().values].index
        for key in na_rows:
            summary.at[key, str(event)] = 0
        summary = summary.assign(**{str(event): summary[str(event)].astype(int)})

    events_str = [str(event) for event in events]
    summary = add_best4_score(summary, events_str)
    return summary
