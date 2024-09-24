import pandas as pd
import ast
from datetime import datetime
import openpyxl

from database.req import create_company

file_path = '/Users/timofejsosnin/Downloads/Lida24.09_as.xlsx' #path to .csv file on your computer
# companies_df = pd.read_csv(file_path)
companies_df = pd.read_excel(file_path)


async def csv_to_db():
    for index, row in companies_df.iterrows():
        try:
            if pd.isna(row['Наименование']) or pd.isna(row['Код основного вида деятельности']) or pd.isna(
                    row['Сайт в сети Интернет']) or pd.isna(row['Электронный адрес']):
                continue
            if not pd.isna(row['Дата регистрации']):
                today = datetime.now().year
                date = int(str(row['Дата регистрации'])[0:4])
                age = today - date
            else:
                age = -1
            data = {
                'company_name': row['Наименование'],
                # 'okveds': ast.literal_eval(row['Код основного вида деятельности']),
                'okveds': row['Код основного вида деятельности'],
                'inn': int(row['ИНН']) if not pd.isna(row['ИНН']) else -1,
                # 'description': ast.literal_eval(row['Sites'])[0] if len(ast.literal_eval(row['Sites'])) > 0 else '-1',
                'description': row['Сайт в сети Интернет'] if not pd.isna(row['Сайт в сети Интернет']) else '-1',
                'number_employees': (int(row['2023, Среднесписочная численность работников']) if type(row['2023, Среднесписочная численность работников']) != str else int(row['2023, Среднесписочная численность работников'].replace(" ", "").replace("\u00A0", ""))) if not pd.isna(
                    row['2023, Среднесписочная численность работников']) else -1,
                # 'registration_form': int(row['Okopf']) if not pd.isna(row['Okopf']) else -1,
                'number_years_existence': age,
                'revenue_last_year': (int(row['2023, Выручка, RUB']) if type(row['2023, Выручка, RUB']) != str else int(row['2023, Выручка, RUB'].replace(" ", "").replace("\u00A0", ""))) if not pd.isna(row['2023, Выручка, RUB']) else -1,
                # 'site': ast.literal_eval(row['Sites'])[0] if len(ast.literal_eval(row['Sites'])) > 0 else '-1',
                'site': row['Сайт в сети Интернет'] if not pd.isna(row['Сайт в сети Интернет']) else '-1',
                # 'company_mail': ast.literal_eval(row['Emails'])[0] if len(ast.literal_eval(row['Emails'])) > 0 else '-1',
                'company_mail': row['Электронный адрес'] if not pd.isna(row['Электронный адрес']) else '-1',
                # 'company_tel': ast.literal_eval(row['Phones'])[0] if ((not pd.isna(row['Phones'])) and len(ast.literal_eval(row['Phones']))) > 0 else '-1',
            }
            await create_company(data)
        except Exception as e:
            print("=====\n"*3, e, '\n', "=====\n"*3)
