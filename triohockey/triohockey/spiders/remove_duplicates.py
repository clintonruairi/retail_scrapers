import pandas as pd


csv = pd.read_csv('triohockeyv4.csv')
print(len(csv))

new_csv = csv.drop_duplicates(keep='first') # keep only first occurence of duplicate

print(len(new_csv))

new_csv.to_csv('triohockeyv4_.csv')