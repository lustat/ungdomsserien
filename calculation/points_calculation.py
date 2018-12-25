import pandas as pd


def add_points_to_event_result(res, class_selection=None, region_id=16):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    competition_class = [classname in class_selection for classname in res['classname']]
    compres = res.loc[competition_class]
    
    # Pick out runners from Skåne
    regrun = region_runners(compres)

    results = add_points_to_competion_class(regrun)
    return results

def add_points_to_competion_class(res):
    res = res.reset_index(drop=True, inplace=False)  #Make sure runners (i.e. rows) have unique index
    res = res.assign(points=0)

    for (key, runner) in res.iterrows():
        if runner.finished:
            points = max(30 - int(runner.region_position) + 1, 10)
        else:
            if runner.started:
                points = 5
            else:  # runner did not start
                points = 0
        res.at[key, 'points'] = points

    return res


def region_runners(df, region_id=16):
    df = df.assign(region=df.region.astype('int'))
    region_runners = df.loc[df.region == region_id]


    region_runners_finished = region_runners.loc[region_runners.finished]
    region_runners_notfinished = region_runners.loc[(~region_runners.finished) & (region_runners.started)]

    region_runners_finished = region_runners_finished.assign(position=region_runners_finished.position.astype('int'))
    region_runners_notfinished = region_runners_notfinished.assign(position=0, region_position=0)

    df_all = pd.DataFrame()
    for cname in region_runners_finished.classname.unique():
        df0 = region_runners_finished.loc[region_runners_finished.classname == cname]
        df0 = df0.reset_index(drop=True, inplace=False)
        df0 = df0.assign(region_position=df0.index + 1)

        # Append started but not finished runners
        df_notfin = region_runners_notfinished.loc[region_runners_notfinished.classname == cname]
        df0 = df0.append(df_notfin)
        if df_all.empty:
            df_all = df0.copy()
        else:
            df_all = df_all.append(df0)

    return df_all

