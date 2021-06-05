import pandas as pd


csv = pd.read_csv("file.csv")
len(csv)
new_csv = csv[csv.duplicated()] # show duplicates

new_csv = csv.drop_duplicates(keep='first') # keep only first occurence of duplicate

len(new_csv)