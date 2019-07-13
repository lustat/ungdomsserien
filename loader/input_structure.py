import pandas as pd
import numpy as np
import os
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Color


def get_input_structure():
    event_ids = [20550, 21406, 21376, 21988, 21732, 21644]
    df_parameters = pd.DataFrame(data={'Parameter': ['event_ids', 'night_ids'],
                                       'Value': ['20550, 21406, 21376, 21988, 21732, 21644', '21851, 21961']})

    dct_parameters = {'example_df': df_parameters,
                      'compulsory': True,
                      'description': 'Listar input-parametrar till beräkning (t ex Event ID)'}

    division = list(np.tile(['Elit'], 6))
    division.extend(list(np.tile(['Division 1'], 7)))
    division.extend(list(np.tile(['Division 2'], 7)))
    division.extend(list(np.tile(['Division 3'], 4)))
    club_id = [483, 639, 125, 258, 471, 114, 35, 614, 54, 487, 167, 169,
               507, 165, 81, 111, 294, 461, 400, 558, 132, 331, 544, 228]

    club_name = ['Lunds OK', 'Skåneslättens OL', 'Helsingborgs SOK', 'Malmö OK', 'Örkelljunga FK', 'FK Göingarna',
                 'Andrarums IF', 'Hjärnarps OL', 'FK Boken', 'OK Tyringe', 'Hässleholms OK', 'Hästveda OK',
                 'OK Kontinent', 'Härlövs IF', 'Frosta OK', 'OK Gynge', 'OK Pan-Kristianstad', 'FK Åsen',
                 'Tormestorps IF', 'OK Kompassen', 'Eslövs FK', 'IS Skanne', 'Ystads OK', 'IS Kullen']

    df_division = pd.DataFrame(data={'Division': division,
                                     'Clubid': club_id,
                                     'Club': club_name})

    dct_division = {'example_df': df_division,
                    'compulsory': False,
                    'description': 'Anger divisionstillhörighet for respektive klubb'}

    df_event = pd.DataFrame(data={'Name': ['Förnamn1 Efternamn1', 'Förnamn2 Efternamn2'], 'Class': ['U1', 'Inskolning'],
                                  'Club': ['Skåneslättens OL', 'Lunds OK']})
    dct_event = {'example_df': df_event,
                 'compulsory': False,
                 'description': 'Anger namn på tävlande med okänd ålder som ska räknas'}

    df_night = pd.DataFrame(data={'Person ID': ['11111', '222222'],
                                  'Name': ['Förnamn1 Efternamn1', 'Förnamn2 Efternamn2'],
                                  'Club': ['Skåneslättens OL', 'Lunds OK'],
                                  'U-series': ['D12', 'H14'],
                                  'Night-class': ['U2', 'Öppen Motion 5'],
                                  'Event ID': [21930, 22921],
                                  'Finished': [1, 0]})
    dct_night = {'example_df': df_night,
                 'compulsory': False,
                 'description': 'Anger deltagande i natt-tävling, i natt-tävlingar som inte listats via "night_ids" i "Parameters"-flik.'}


    structure = {'Parameters': dct_parameters,
                 'Division': dct_division,
                 str(event_ids[0]): dct_event,
                 'Night': dct_night}
    return structure


def create_excel_template(structure, template_path=''):
    # TODO get storage path
    if not template_path:
        # Debug
        template_path = os.getcwd()

    excel_name = 'Input_Example.xlsx'
    excel_file = os.path.join(template_path, excel_name)

    wb = openpyxl.Workbook()
    standard_sheets = wb.get_sheet_names()
    for sheet in structure.keys():
        worksheet = wb.create_sheet(sheet)
        df = structure[sheet]['example_df']

        for r in dataframe_to_rows(df, index=False, header=True):
            worksheet.append(r)

    # Remove standard sheets
    for standard_sheet in standard_sheets:
        std = wb.get_sheet_by_name(standard_sheet)
        wb.remove(std)

    wb.save(excel_file)
    print('Skapar exempel-fil enligt mall: ' + excel_file)
    return excel_file


if __name__ == '__main__':
    template = get_input_structure()
    file = create_excel_template(structure=template)

    print('Finished')