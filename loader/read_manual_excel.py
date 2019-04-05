import pandas as pd
import os
import sys
import xlrd


def get_excel_sheets(excel_file):
    excel_work_book = xlrd.open_workbook(excel_file)
    return excel_work_book.sheet_names()


def check_sheet_names(sheet_names):
    ok_sheets = []

    for original_sheet in sheet_names:
        sheet = original_sheet.replace(' ', '')
        if sheet.isdigit():
            ok_sheets.append(original_sheet)
        else:
            if (sheet.lower().startswith('night')) | (sheet.lower().startswith('natt')):
                ok_sheets.append(original_sheet)
    return ok_sheets


def read_manual_input(manual_input_file='C:\\Users\\Klas\\Desktop\\Manuell lista.xlsx'):
    if not os.path.exists(manual_input_file):
        sys.exit('Input file is not found: ' + manual_input_file)

    all_sheets = get_excel_sheets(manual_input_file)
    accepted_sheets = check_sheet_names(all_sheets)

    race_to_manual_input = {}
    for sheet in accepted_sheets:
        df = pd.read_excel(manual_input_file, sheet)
        sheet = sheet.replace(' ', '')
        df.columns = [col.lower() for col in df.columns]
        if sheet.isdigit():
            race_to_manual_input[int(sheet)] = df
        else:
            race_to_manual_input['night'] = df

    return race_to_manual_input


if __name__=='__main__':
    dct = read_manual_input()
    print(dct)