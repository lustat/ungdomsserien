import pandas as pd
from calculation.calc_utils import valid_open_runners


def add_night_points_to_event(res, class_selection=None, region_id=16):
    if class_selection is None:
        class_selection = ['H12', 'H14', 'H16', 'D12', 'D14', 'D16']

    competition_class = [classname in class_selection for classname in res['classname']]
    open_short_class = [not (classname in class_selection) for classname in res['classname']]

    compres = res.loc[competition_class]
    openres = res.loc[open_short_class]

    # Pick out runners from Skåne
    region_competition = region_runners(compres)
    region_open = valid_open_runners(openres)

    results1 = points_to_started_night(region_competition)
    results2 = points_to_started_night(region_open)

    results = results1.append(results2, sort=False)
    return results


def add_points_to_event(res, class_selection=None, region_id=16):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    competition_class = [classname in class_selection for classname in res['classname']]
    open_short_class = [not (classname in class_selection) for classname in res['classname']]

    compres = res.loc[competition_class]
    openres = res.loc[open_short_class]
    
    # Pick out runners from Skåne
    region_competition = region_runners(compres)
    region_open = valid_open_runners(openres)

    results1 = add_points_to_competion_class(region_competition)
    results2 = points_to_started_open(region_open)

    results = results1.append(results2, sort=False)
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
        for pid in df0.personid.unique():
            person=df0.loc[df0.personid==pid]

        df0 = df0.assign(region_position=df0.index + 1)

        # Append started but not finished runners
        df_notfin = region_runners_notfinished.loc[region_runners_notfinished.classname == cname]
        df0 = df0.append(df_notfin)
        if df_all.empty:
            df_all = df0.copy()
        else:
            df_all = df_all.append(df0)

    return df_all


def points_to_started_open(df, region_id=16):
    df = df.assign(region=df.region.astype('int'))
    df = df.loc[df.region == region_id]

    df = df.assign(region_position=0, points=0)
    df_fin = df.loc[df.finished]
    df_sta = df.loc[~df.finished]

    df_fin = df_fin.assign(points=10)
    df_sta = df_sta.assign(points=5)
    df_out = df_fin.append(df_sta, sort=False)
    return df_out


def points_to_started_night(df, region_id=16):
    df = df.loc[df.started]  #Remove not started

    df = df.assign(region=df.region.astype('int'))
    df = df.loc[df.region == region_id]

    df = df.assign(region_position=0, points=0)
    df_fin = df.loc[df.finished]
    df_sta = df.loc[~df.finished]

    df_fin = df_fin.assign(points=10)
    df_sta = df_sta.assign(points=5)
    df_out = df_fin.append(df_sta, sort=False)
    return df_out