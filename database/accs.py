import pandas as pd

from database.req import create_acc

file_path = '/Users/timofejsosnin/PycharmProjects/lida/lida/database/accs.csv'


async def accs_to_db():
    accs_df = pd.read_csv(file_path)
    for i, row in accs_df.iterrows():
        data = {'email': row[0], 'password': row[1]}
        await create_acc(data)
