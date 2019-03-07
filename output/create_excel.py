import pandas as pd
import os


def individual_results_excel(storage_path, dct):
    if dct:  # if dictionary is non-empty
        # One Excel sheet per class
        excel_file = os.path.join(storage_path, 'IndividualResults.xlsx')
        writer = pd.ExcelWriter(excel_file)
        for class_name in dct.keys():
            df = dct[class_name]
            df = df.set_index(keys='position', drop=True, inplace=False)
            df.to_excel(writer, class_name, index=True)

        print('Saving ' + excel_file)
        writer.save()
        return excel_file


def club_results_excel(storage_path, df, club_results):
    if not df.empty:
        excel_file = os.path.join(storage_path, 'ClubResults.xlsx')
        writer = pd.ExcelWriter(excel_file)
        df.to_excel(writer, 'Summary', index=False)
        for club_result in club_results:
            if not club_result.empty:
                club_result.to_excel(writer, club_result.iloc[0].club, index=False)
        print('Saving ' + excel_file)
        writer.save()
        return excel_file
