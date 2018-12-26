def summarize_compclasses(class_selection=None):
    if class_selection is None:
        class_selection = ['H10', 'H12', 'H14', 'H16', 'D10', 'D12', 'D14', 'D16']

    for classname in class_selection:
        print(classname)