import pandas as pd
import ast
from datetime import datetime

from database.req import create_company

file_path = '/Users/timofejsosnin/Downloads/companies_data.csv' #path to .csv file on your computer
companies_df = pd.read_csv(file_path)

async def csv_to_db():
    for index, row in companies_df.iterrows():
        if pd.isna(row['Name']) or pd.isna(row['ActivityTypes']) or pd.isna(row['Sites']) or pd.isna(row['Emails']):
            continue
        if not pd.isna(row['RegistrationDate']):
            today = datetime.now().year
            date = int(row['RegistrationDate'][0:4])
            age = today - date
        else: age = -1
        data = {
            'company_name': row['Name'],
            'okveds': ast.literal_eval(row['ActivityTypes']),
            'inn': int(row['Inn']) if not pd.isna(row['Inn']) else -1,
            'description': ast.literal_eval(row['Sites'])[0] if len(ast.literal_eval(row['Sites'])) > 0 else '-1',
            'number_employees': int(row['EmployeesCount']) if not pd.isna(row['EmployeesCount']) else -1,
            'registration_form': int(row['Okopf']) if not pd.isna(row['Okopf']) else -1,
            'number_years_existence': age,
            'revenue_last_year': int(row['Capital']) if not pd.isna(row['Capital']) else -1,
            'site': ast.literal_eval(row['Sites'])[0] if len(ast.literal_eval(row['Sites'])) > 0 else '-1',
            'company_mail': ast.literal_eval(row['Emails'])[0] if len(ast.literal_eval(row['Emails'])) > 0 else '-1',
            'company_tel': ast.literal_eval(row['Phones'])[0] if ((not pd.isna(row['Phones'])) and len(ast.literal_eval(row['Phones']))) > 0 else '-1',
        }

        await create_company(data)
