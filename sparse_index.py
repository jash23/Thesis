import pandas as pd

df = pd.read_csv('components.csv')
df1 = df.filter(['K', 'P'])
df1.to_csv('sparse_index.csv', index=False)

