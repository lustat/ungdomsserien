import pandas as pd
import os
from datetime import datetime
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Color


def individual_results_excel(storage_path, dct):
    if dct:  # if dictionary is non-empty
        # One Excel sheet per class
        today = datetime.today().strftime('%y%m%d')
        excel_name = 'IndividualResults_' + today + '.xlsx'
        excel_file = os.path.join(storage_path, excel_name)

        wb = openpyxl.Workbook()
        standard_sheets = wb.get_sheet_names()
        for class_name in dct.keys():
            worksheet = wb.create_sheet(class_name)

            df = dct[class_name]
            if not df.empty:
                if sum(df.night) == 0:
                    df = df.drop(columns=['night'])

                if all(df.score == df.total):
                    df = df.drop(columns=['score'])

                for r in dataframe_to_rows(df, index=False, header=True):
                    worksheet.append(r)

                for (df_col, col) in zip(df.columns, worksheet.columns):
                    column = col[0].column
                    header_cell = col[0]
                    header_cell.font = Font(bold=True)
                    if isinstance(df[df_col].iloc[0], str):
                        adjusted_width = 1.4 * df[df_col].str.len().max()
                        adjusted_width = min(adjusted_width, 40)
                    elif isinstance(df[df_col].iloc[0], int) | isinstance(df[df_col].iloc[0], float):
                        adjusted_width = 10
                    else:
                        adjusted_width = 10
                    # print(str(df_col) + ': ' + str(adjusted_width))
                    worksheet.column_dimensions[column].width = adjusted_width

                # Freeze panes
                c = worksheet['B2']
                worksheet.freeze_panes = c

        # Remove standard sheets
        for standard_sheet in standard_sheets:
            std = wb.get_sheet_by_name(standard_sheet)
            wb.remove(std)

        wb.save(excel_file)
        print('Sparar ' + excel_file)
        return excel_file


def club_results_to_excel(storage_path, df, club_results):
    def create_summary_with_division(worksheet, data):
        previous_division = ''
        for row in dataframe_to_rows(data, index=False, header=True):
            current_division = row[-1]
            if previous_division:
                if current_division == previous_division:
                    worksheet.append(row[:-1])
                else:
                    empty_row = [' ' for str in row]
                    worksheet.append(empty_row)
                    title_row = empty_row
                    title_row[0] = current_division
                    worksheet.append(title_row)
                    worksheet.append(row[:-1])
            else:
                worksheet.append(row[:-1])
            previous_division = current_division

    def create_summary_without_division(worksheet, data):
        for row in dataframe_to_rows(data, index=False, header=True):
            worksheet.append(row[:-1])

    if df.empty:
        return None
    else:
        today = datetime.today().strftime('%y%m%d')
        excel_name = 'ClubResults_' + today + '.xlsx'
        excel_file = os.path.join(storage_path, excel_name)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Summary"
        df = df.reset_index(drop=True, inplace=False)

        if all(df.division.isna()):
            create_summary_without_division(ws, df)
        else:
            create_summary_with_division(ws, df)

        for (df_col, col) in zip(df.columns, ws.columns):
            column = col[0].column
            header_cell = col[0]
            header_cell.font = Font(bold=True)
            if isinstance(df[df_col].iloc[0], str):
                adjusted_width = 1.4 * df[df_col].str.len().max()
                if adjusted_width < 10:
                    adjusted_width = 10
            elif isinstance(df[df_col].iloc[0], int) | isinstance(df[df_col].iloc[0], float):
                adjusted_width = 30
            else:
                adjusted_width = 10
            ws.column_dimensions[column].width = adjusted_width

        for club_result in club_results:
            if not club_result.empty:
                if 'name' in club_result.columns:
                    name_first_list = ['name']
                    name_first_list.extend([col for col in club_result.columns if col != 'name'])
                    club_result = club_result[name_first_list]

                ws = wb.create_sheet(club_result.iloc[0].club)
                for r in dataframe_to_rows(club_result, index=False, header=True):
                    ws.append(r)

                for (df_col, col) in zip(club_result.columns, ws.columns):
                    column = col[0].column
                    header_cell = col[0]
                    header_cell.font = Font(bold=True)
                    if isinstance(club_result[df_col].iloc[0], str):
                        adjusted_width = 1.4 * club_result[df_col].str.len().max()
                    else:
                        adjusted_width = 10
                    ws.column_dimensions[column].width = adjusted_width

                # Freeze panes
                c = ws['B2']
                ws.freeze_panes = c
        wb.save(excel_file)
        print('Sparar ' + excel_file)
        return excel_file

