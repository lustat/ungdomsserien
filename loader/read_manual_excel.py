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


def check_columns_in_sheets(excel_file, sheets):
    day_columns = ['name', 'class', 'club']
    night_columns = ['personid', 'name', 'club', 'useries', 'nightclass', 'eventid', 'finished']
    filename = os.path.split(excel_file)[1]
    print('Kollar kolumner i ' + filename)
    column_missing = False
    for sheet in sheets:
        df = pd.read_excel(excel_file, sheet)
        current_columns = [col.lower().replace(' ', '').replace('-', '') for col in df.columns]
        if sheet.replace(' ', '').isdigit():
            for column in day_columns:
                if not (column in current_columns):
                    print('Varning: ' + column + ' saknas i ' + sheet)
                    column_missing = True
        else:
            for column in night_columns:
                if not (column in current_columns):
                    print('Varning: ' + column + ' saknas i ' + sheet)
                    column_missing = True
    if not column_missing:
        print('Ingen kolumn saknas i Excel-fil')
        print(' ')


def read_manual_input(manual_input_file='C:\\Users\\Klas\\Desktop\\Manual results.xlsx'):
    race_to_manual_input = {}
    if not os.path.exists(manual_input_file):
        if manual_input_file:
            print('Ingen Excel-fil identifierad: ' + manual_input_file)
        else:
            print('Ingen Excel-fil vald')
    else:
        all_sheets = get_excel_sheets(manual_input_file)
        accepted_sheets = check_sheet_names(all_sheets)
        check_columns_in_sheets(manual_input_file, accepted_sheets)

        for sheet in accepted_sheets:
            df = pd.read_excel(manual_input_file, sheet)
            sheet = sheet.replace(' ', '')
            df.columns = [col.lower().replace(' ', '').replace('-', '') for col in df.columns]
            if sheet.isdigit():
                race_to_manual_input[int(sheet)] = df
            else:
                race_to_manual_input['night'] = df

    return race_to_manual_input


if __name__ == '__main__':
    dct = read_manual_input()
    print(dct)
