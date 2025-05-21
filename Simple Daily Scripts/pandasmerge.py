#Merge two pandas data frames, change values before use
import pandas as pd

df1 = pd.read_csv('changethis1.csv')
df2 = pd.read_csv('changethis2.csv')

merged = pd.merge(df1, df2, on='changethisalso', how='inner')
merged.to_csv('merged_sheet.csv', index=False)