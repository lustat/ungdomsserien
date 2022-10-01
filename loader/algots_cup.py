import os
import datetime
import pandas as pd

from loader.read_manual_excel import read_manual_input
from loader.read_results import extract_and_analyse

if __name__ == "__main__":
    # manual, club_division, user_dct = read_manual_input(manual_input_file='C:\\Users\\Klas\\Desktop\\Example_inputs\\Manual_input_2021.xlsx')
    print('Älgots Cup 2022: 34537)')

    manual = pd.DataFrame()
    storage_path = os.getcwd() + '/algots_cup_' + datetime.datetime.now().strftime('%H%M%S')
    os.makedirs(storage_path, exist_ok=True)
    club_division = pd.DataFrame()
    user_dct = {}
    event_id = '34537'

    user_dct['night_ids'] = ''
    extract_and_analyse(storage_path=storage_path, race_to_manual_info=manual,
                        club_division_df=club_division, user_input=user_dct)
