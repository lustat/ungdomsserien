def add_points_to_event_result(res, class_selection=None):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    competition_class = [classname in class_selection for classname in res['class']]
    compres = res.loc[competition_class]

    compres = add_points_to_coempetion_class(compres)


def add_points_to_coempetion_class(res):
