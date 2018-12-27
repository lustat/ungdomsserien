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

    writer.save()

def club_results_excel(dct):
    print(dct)