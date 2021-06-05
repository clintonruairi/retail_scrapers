import pandas as pd

df = pd.read_csv('spiders/bathandbodyMay.csv')

def format_ea(df):
    count = 0
    for row in df['category']:
        if type(row) == str:
            if '-' in row:
                df.iloc[count, 3] = str(df.iloc[count, 3]).replace('-', ' ')
                print(df.iloc[count, 3])
                
            #df.iloc[count, 6] = str(df.iloc[count, 7]).upper() # df.iloc[row_number, column_number]
            #df.iloc[count, 7] = None # 6 = price unit column
                count += 1
    print(count)

format_ea(df)
df.to_csv('bathandbodyMayv2.csv', index=False)