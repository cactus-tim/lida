import pandas as pd
import os

from database.req import create_acc

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'accs.csv')


async def accs_to_db():
    accs_df = pd.read_csv(file_path)
    for i, row in accs_df.iterrows():
        data = {'email': str(row[0]).strip(), 'password': str(row[1]).strip()}
        await create_acc(data)
