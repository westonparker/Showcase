#uses fuzz to detect duplicate data in csvs
import pandas as pd
from fuzzywuzzy import fuzz

df = pd.read_csv('changethis.csv')

dupes = []

for i in range(len(df)):
    for j in range(i + 1, len(df)):
        #change depending on use case
        if fuzz.ratio(df.loc[i, 'name'], df.loc[j, 'name']) > 90:
            dupes.append((i, j))

print("Possible duplicates:", dupes)
