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
        if runner.classname.lower().startswith('ö'):
            if runner.birthyear is not None:
                if (runner.age <= 16) & (runner.age >= 5):
                    include = True
        else:  #"inskolning" or U-class
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
    print(manual_df)
    print(night_df)
