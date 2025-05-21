#Detects outliers in a file, change parameters before use. 

import pandas as pd

df = pd.read_csv('data.csv')

q1 = df['value'].quantile(0.25) 
q3 = df['value'].quantile(0.75) 

iqr = q3 - q1
filtered = df[(df['value'] >= q1 - 1.5 * iqr) & (df['value'] <= q3 + 1.5 * iqr)]
filtered.to_csv('no_outliers.csv', index=False)