import pandas as pd

df = pd.read_csv('thebodyshopMay.csv')

def format_ea(df):
    count = 0
    for row in df['category']:
        if type(row) == str:
            if '-' in row:
                df.iloc[count, 3] = row.replace('-', ' ')
                print(row)
            #df.iloc[count, 6] = str(df.iloc[count, 7]).upper() # df.iloc[row_number, column_number]
            #df.iloc[count, 7] = None # 6 = price unit column
        count += 1
    print(count)