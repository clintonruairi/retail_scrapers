import pandas as pd

df = pd.read_csv('spiders/thebodyshopMay.csv')
print(df)
def format_ea(df):
    count = 0
    for row in df['average_rating']:
        if type(row) == str:
            print(row)
            print(str(df.iloc[count, 12]).upper()) # 7 = size column
            #df.iloc[count, 6] = str(df.iloc[count, 7]).upper() # df.iloc[row_number, column_number]
            #df.iloc[count, 7] = None # 6 = price unit column
        count += 1