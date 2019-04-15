import numpy as np
import pandas as pd


def valid_open_runners(df, manual=pd.DataFrame()):
    if not manual.empty:
        manual = manual.assign(simplename=[name.replace(' ', '').lower() for name in manual.name])
        manual = manual.assign(simpleclub=[name.replace(' ', '').lower() for name in manual.club])
        manual = manual.assign(identified=False)

    df = df.loc[df.started]  # Keep only started
    df = df.reset_index(drop=True, inplace=False)  # Make sure runners (i.e. rows) have unique index
    for (key, runner) in df.iterrows():
        include = False
        if runner.birthyear is not None:
            if (runner.age <= 16) & (runner.age >= 5):
                include = True
            elif (np.isnan(runner.age)) & (not manual.empty):  # unknown birth year: Look in manual information
                runner_match = manual.loc[(manual.simplename == runner['name'].replace(' ', '').lower()) &
                                          (manual.simpleclub == runner['club'].replace(' ', '').lower())]
                if not runner_match.empty:
                    if len(runner_match) == 1:
                        include = True
                        manual.at[runner_match.index, 'identified'] = True
                    else:
                        print('Löpare ' + runner['name'] + ' är listad på flera ställen')
        df.at[key, 'include'] = include

    if not manual.empty:
        manual = manual.drop(columns=['simplename', 'simpleclub'], inplace=False)
        un_identified = manual.loc[~manual.identified]
    else:
        un_identified = pd.DataFrame()

    df = df.loc[df.include]
    df = df.drop(columns=['include'])
    return df, un_identified


def add_manual_night_runners(manual_df, night_df):
    night_df = night_df.reset_index(drop=True, inplace=False)
    columns = list(night_df.columns)
    for (key, row) in manual_df.iterrows():
        new_key = len(night_df)
        row = pd.Series()
        row.at['event_year'] = 0
        row.at['classname'] = manual_df.loc[key, 'useries']
        row.at['name'] = manual_df.loc[key, 'name']
        row.at['personid'] = manual_df.loc[key, 'personid']
        row.at['birthyear'] = 0
        row.at['age'] = 0
        row.at['orgid'] = 0
        row.at['club'] = manual_df.loc[key, 'club']
        row.at['region'] = 0
        row.at['started'] = True
        row.at['finished'] = manual_df.loc[key, 'finished']==1
        row.at['position'] = 0
        row.at['seconds'] = 0
        row.at['region_position'] = 0
        if row.at['finished']:
            row.at['points'] = 10
        else:
            row.at['points'] = 5
        row.at['eventid'] = manual_df.loc[key, 'eventid']
        row.name = new_key
        night_df = night_df.append(row, ignore_index=True)
    return night_df


def add_person_id(manual_df, daily_df):
    daily_df = daily_df.assign(simplename=[name.replace(' ', '').lower() for name in daily_df.name])
    daily_df = daily_df.assign(simpleclub=[name.replace(' ', '').lower() for name in daily_df.club])
    manual_df = manual_df.reset_index(drop=True, inplace=False)
    manual_df = manual_df.assign(personid=0)
    for (key, runner) in manual_df.iterrows():
        identified = daily_df.loc[(runner['name'].replace(' ','').lower() == daily_df.simplename) &
                     (runner['club'].replace(' ','').lower() == daily_df.simpleclub)]
        if not identified.empty:
            manual_df.at[key, 'personid'] = identified['personid'].iloc[0]
    return manual_df
