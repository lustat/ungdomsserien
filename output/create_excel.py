import pandas as pd
import os
from datetime import datetime
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Color
from openpyxl.styles.borders import Border, Side


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

                if 'position' in df.columns:
                    new_column_order = ['position']
                    columns = list(df.columns)
                    columns.remove('position')
                    new_column_order.extend(columns)
                    df = df[new_column_order]

                for r in dataframe_to_rows(df, index=False, header=True):
                    worksheet.append(r)

                for (df_col, col) in zip(df.columns, worksheet.columns):
                    column = col[0].column
                    header_cell = col[0]
                    header_cell.font = Font(bold=True)
                    if isinstance(df[df_col].iloc[0], str):
                        adjusted_width = 1.4 * df[df_col].str.len().max()
                        adjusted_width = min(adjusted_width, 40)
                        adjusted_width = max(adjusted_width, 8)
                    elif isinstance(df[df_col].iloc[0], int) | isinstance(df[df_col].iloc[0], float):
                        adjusted_width = 10
                    else:
                        adjusted_width = 10
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
    def add_line_flag(data):
        data = data.assign(position=0)
        data = data.assign(negative_position=0)
        for (key, row) in data.iterrows():
            division_data = data.loc[data.division == row.division]
            data.at[key, 'position'] = 1 + sum(row.score < division_data.score)
            data.at[key, 'negative_position'] = sum(row.score > division_data.score)

        data = data.assign(line_above=False)
        for division in data.division.unique():
            division_data = data.loc[data.division == division]
            if len(division_data) >= 4:
                third_position = division_data.loc[division_data.position == 3]
                if len(third_position) == 1:
                    if division.lower() != 'elit':
                        data.at[third_position.index[0], 'line_above'] = True

                second_last = division_data.loc[division_data.negative_position == 1]
                if len(second_last) == 1:
                    if division.lower() != 'division 3':
                        data.at[second_last.index[0], 'line_above'] = True

        data = data.drop(columns={'position', 'negative_position'})
        return data

    def create_summary_with_division(worksheet, data):
        previous_division = ''
        last_row_header = True
        for row in dataframe_to_rows(data, index=False, header=True):
            current_division = row[-2]
            line_above = row[-1]
            print_row = row[:-2]
            if previous_division:
                if current_division == previous_division:
                    worksheet.append(print_row)
                    if line_above:
                        for column_number in range(1, len(print_row) + 1):
                            cell = worksheet.cell(worksheet.max_row, column_number)
                            cell.border = Border(top=Side(style='dotted'))
                else:
                    empty_row = [' ' for str in row]
                    if last_row_header:
                        worksheet.append(empty_row)
                        last_row_header = False
                    else:
                        worksheet.append(empty_row)
                        worksheet.append(empty_row)
                    title_row = empty_row
                    title_row[0] = current_division
                    worksheet.append(title_row)
                    cell = worksheet.cell(worksheet.max_row, 1)
                    cell.font = Font(bold=True)
                    worksheet.append(print_row)
            else:
                worksheet.append(print_row)
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
            df = add_line_flag(df)
            create_summary_with_division(ws, df)

        for (df_col, col) in zip(df.columns, ws.columns):
            column = col[0].column
            header_cell = col[0]
            if header_cell.value == 'club':
                header_cell.value = ''
            else:
                header_cell.font = Font(bold=True)
            if isinstance(df[df_col].iloc[0], str):
                adjusted_width = 1.4 * df[df_col].str.len().max()
                if adjusted_width < 10:
                    adjusted_width = 10
            elif isinstance(df[df_col].iloc[0], int) | isinstance(df[df_col].iloc[0], float):
                adjusted_width = 50
            else:
                adjusted_width = 10
            ws.column_dimensions[column].width = adjusted_width

        for club_result in club_results:
            if not club_result.empty:
                if 'name' in club_result.columns:
                    name_first_list = ['name']
                    name_first_list.extend([col for col in club_result.columns if col != 'name'])
                    club_result = club_result[name_first_list]

                do_not_print_columns = ['event_year', 'region', 'birthyear', 'seconds']
                club_result = club_result.drop(columns=do_not_print_columns)

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

