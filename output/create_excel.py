import pandas as pd
import os
from loader.loader_utils import rel2fullpath


def individual_results_excel(dct):
    # One Excel sheet per class
    storage_path = rel2fullpath('output')
    excel_file = os.path.join(storage_path, 'IndividualResults.xlsx')
    writer = pd.ExcelWriter(excel_file)
    for class_name in dct.keys():
        df = dct[class_name]
        df.to_excel(writer, class_name)

    print('Saving ' + excel_file)
    writer.save()
    return excel_file

def club_results_excel(df, club_results):
    storage_path = rel2fullpath('output')
    excel_file = os.path.join(storage_path, 'ClubResults.xlsx')
    writer = pd.ExcelWriter(excel_file)
    df.to_excel(writer, 'Summary')
    for club_result in club_results:
        if not club_result.empty:
            club_result.to_excel(writer, club_result.iloc[0].club, index=False)
    print('Saving ' + excel_file)
    writer.save()
    return excel_file
