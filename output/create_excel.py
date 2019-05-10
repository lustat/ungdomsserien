import pandas as pd
import os
from datetime import datetime


def individual_results_excel(storage_path, dct):
    if dct:  # if dictionary is non-empty
        # One Excel sheet per class
        today = datetime.today().strftime('%y%m%d')
        excel_name = 'IndividualResults_' + today + '.xlsx'
        excel_file = os.path.join(storage_path, excel_name)

        writer = pd.ExcelWriter(excel_file)
        for class_name in dct.keys():
            df = dct[class_name]
            df = df.set_index(keys='position', drop=True, inplace=False)
            df.to_excel(writer, class_name, index=True)

        print('Sparar ' + excel_file)
        writer.save()
        return excel_file


def club_results_excel(storage_path, df, club_results):
    if not df.empty:
        today = datetime.today().strftime('%y%m%d')
        excel_name = 'ClubResults_' + today + '.xlsx'
        excel_file = os.path.join(storage_path, excel_name)
        writer = pd.ExcelWriter(excel_file)
        df.to_excel(writer, 'Summary', index=False)
        for club_result in club_results:
            if not club_result.empty:
                club_result.to_excel(writer, club_result.iloc[0].club, index=False)
        print('Saving ' + excel_file)
        writer.save()
        return excel_file
