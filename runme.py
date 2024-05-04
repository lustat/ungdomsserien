import sys

from dotenv import load_dotenv
import pandas as pd
from loader.read_manual_excel import read_manual_input
from loader.read_results import extract_and_analyse
from definitions import DATA_DIR


if __name__ == "__main__":
    print(f'Running with {sys.version}')
    youth_series = True
    load_dotenv()

    if youth_series:
        manual_input_file = f'{DATA_DIR}/01_input/Manual_input_2024.xlsx'
        manual, club_division, user_dct = read_manual_input(manual_input_file=manual_input_file)
        extract_and_analyse(race_to_manual_info=manual,
                            club_division_df=club_division,
                            user_input=user_dct)
    else:
        # print('Älgots Cup 2021: 32730)')
        # print('Älgots Cup 2022: 34537)')
        # print('Älgots Cup 2023: 46558)')

        use_manual_file = True
        if use_manual_file:
            manual, club_division, user_dct = read_manual_input(
                manual_input_file=f'{DATA_DIR}/01_input/Manual-input-2023-algots.xlsx')
        else:
            manual = pd.DataFrame()
            club_division = pd.DataFrame()
            user_dct = {'event_ids': '46558',
                        'night_ids': ''}

        extract_and_analyse(race_to_manual_info=manual,
                            club_division_df=club_division,
                            user_input=user_dct,
                            algots_cup=True)
