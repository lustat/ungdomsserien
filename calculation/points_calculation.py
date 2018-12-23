def add_points_to_event_result(res, class_selection=None):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    competition_class = [classname in class_selection for classname in res['classname']]
    compres = res.loc[competition_class]

    compres = add_points_to_competion_class(compres)



def add_points_to_competion_class(res):
    res.classname.unique()

    finished_runners = res.loc[res.finished]
    res = res.reset_index(drop=True, inplace=False)  #MAke sure runners (i.e. rows) have unique index
    res = res.assign(points=0)
    for (key, runner) in res.iterrows():
        if runner.finished:
            points = max(30 - int(runner.position) + 1, 10)
        else:
            if runner.started:
                points = 5
            else:  # runner did not start
                points = 0
        res.at['key', 'points'] = points



    return res