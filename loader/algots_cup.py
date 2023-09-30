import os
import datetime
import pandas as pd
from definitions import OUTPUT_DIR

from loader.read_manual_excel import read_manual_input
from loader.read_results import extract_and_analyse

if __name__ == "__main__":
    print('Älgots Cup 2021: 32730)')
    print('Älgots Cup 2022: 34537)')
    print('Älgots Cup 2023: 46558)')
    storage_path = f'{OUTPUT_DIR}/algots_cup_{datetime.datetime.now().year}'

    use_manual_file = True
    if use_manual_file:
        manual, club_division, user_dct = read_manual_input(manual_input_file='C:/PycharmProjects/ungdomsserien/input/Manual-input-2023-algots.xlsx')
    else:
        manual = pd.DataFrame()

        os.makedirs(storage_path, exist_ok=True)
        club_division = pd.DataFrame()
        user_dct = {'event_ids': '46558',
                    'night_ids': ''}

    extract_and_analyse(storage_path=storage_path, race_to_manual_info=manual,
                        club_division_df=club_division, user_input=user_dct)
