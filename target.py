import pandas as pd
import glob
import os

TARGET_COL='days_to_fail'
DB_FOLDER='./db'
DB_2_FOLDER='./db2'

def recalc_target(file, force = False):
    df = pd.read_csv(file)

    if force == True:
        df = df.drop(labels=TARGET_COL, errors='ignore')
        
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(axis=1, how='all')

    if TARGET_COL not in df:
        df[TARGET_COL] = None
    
    for id, failure in df[(df['failure'] == 1) & (df[TARGET_COL] is not None)].iterrows():
        for iid, row in df[df['serial_number'] == failure['serial_number']].iterrows():
            if row['failure'] == 1:
                df.loc[iid, TARGET_COL] = 0
                continue

            delta = (failure['date'] - row['date']).days
            df.loc[iid, TARGET_COL] = delta


    
    if not os.path.exists(DB_2_FOLDER):
        os.makedirs(DB_2_FOLDER)
    
    df.to_csv(DB_2_FOLDER + '/' + os.path.basename(file), index=False)


def calc():
    mask = DB_FOLDER + "/*.csv"
    csv_files = glob.glob(mask)
    if not csv_files:
        raise FileNotFoundError("Не найдено файлов .csv в указанном каталоге.")
    
    print(f"Началось расcчитывание базы данных в {mask}")

    # Формирование БД
    i = 0
    total = len(csv_files)
    for file in csv_files:
        recalc_target(file)
        i = i + 1
        print(f"Расcчитано моделей дисков: {i} из {total}")
