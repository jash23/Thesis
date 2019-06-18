import pandas as pd

df = pd.read_csv('components.csv')
df11 = pd.read_csv('demands.csv')
df12 = pd.read_csv('costs.csv')

# components
df1 = df.filter(['K'])
df2 = df1.drop_duplicates('K')
df2 = df2.sort_values('K')
df2.to_csv('set_of_components.csv', index=False)

# processes
df3 = df.filter(['P'])
df3 = df3.drop_duplicates('P')
df3 = df3.sort_values('P')
df3.to_csv('set_of_processes.csv', index=False)

# r_x
df['freq'] = df.groupby('P')['P'].transform('count')-1
df4 = df[df['EP'] == 1].merge(df[df['EP'] != 1], on=['P'], how='left')
df4.index += 1
df4['C'] = df4.index
df4 = df4[~df4.K_y.isna()]
df5 = df4.filter(['K_x', 'P', 'C', 'R_x'])
df5.columns = ['K', 'P', 'C', 'r_x']

df5.to_csv('r_x.csv', index=False)

# r_y
df6 = df4.filter(['K_y', 'P', 'C', 'R_y'])
df6.columns = ['K', 'P', 'C', 'r_y']
#df6['r_y'] = df6['r_y'].abs()
df6.to_csv('r_y.csv', index=False)

# C
df7 = df4.filter(['C'])
df7.to_csv('C.csv', index=False)

# N
df8 = df.filter(['N'])
df8 = df8.drop_duplicates('N')
df8 = df8.sort_values('N')
df8.to_csv('N.csv', index=False)

# param_f
df9 = df4.filter(['K_x', 'P', 'C'])
df9.columns = ['K', 'P', 'C']
df9['f'] = 1
df9.to_csv('param_f.csv', index=False)

# param_g
df10 = df4.filter(['K_y', 'P', 'C'])
df10.columns = ['K', 'P', 'C']
df10['g'] = 1
df10.to_csv('param_g.csv', index=False)

# param_d
# df13 = df11[df11['Site'] == 9876]
# df13 = df13[df13['Type'] == 10]
df13 = df11.filter(['Component', '2015'])
df13 = df13.groupby('Component').sum().reset_index()
df13.columns = ['K', 'd']
df13['d'] = df13['d']/1000
df13 = df13.sort_values('K')
df37 = df13[df13['K'].isin(df2['K'])]
df37.to_csv('param_d.csv', index=False)

# param_a
df14 = df12.filter(['Component', 'SpecificCM1'])
df14 = df14.groupby('Component').sum().reset_index()
df14.columns = ['K', 'a']
df14['a'] = df14['a']/1000
df14 = df14.sort_values('K')
df36 = df14[df14['K'].isin(df2['K'])]
df36.to_csv('param_a.csv', index=False)

# param_e (all outputs)
df15 = df[df['R'] > 0]
df15 = df15.filter(['K', 'P'])
df15['e'] = 1
df15 = df15.sort_values('K')
df15.to_csv('param_e.csv', index=False)

# param_h (all inputs)
df16 = df[df['R'] < 0]
df16 = df16.filter(['K', 'P'])
df16['h'] = 1
df16 = df16.sort_values('K')
df16.to_csv('param_h.csv', index=False)

# set T
df17 = pd.read_csv('param_e.csv')
df18 = pd.read_csv('param_h.csv')
df19 = pd.merge(df17, df18, how='inner', on='K')
df19 = df19.filter(['K'])
df19 = df19.drop_duplicates('K')
df19.columns = ['T']
df19.to_csv('set_of_transfers.csv', index=False)

# param_j (components having demands and only +R)
df20 = df[df['R'] < 0]
df21 = df[~df['K'].isin(df20['K'])]
df21 = df21.filter(['K', 'P'])
df22 = df21[df21['K'].isin(df37['K'])]
df22['j'] = 1
df22 = df22.sort_values('K')
df22.to_csv('param_j.csv', index=False)

# param_i (components having demands and -R)
df24 = df[df['R'] < 0]
df25 = df24[df24['K'].isin(df37['K'])]
df25 = df25.filter(['K'])
df25['i'] = 1
df25 = df25.drop_duplicates('K')
df25 = df25.sort_values('K')
df25.to_csv('param_i.csv', index=False)

# param_l
df26 = df37.filter(['K'])
df26['l'] = 1
df26.to_csv('param_l.csv', index=False)

# param_u
df27 = df.filter(['EP', 'P', 'u'])
df27 = df27[df27['EP'] == 1]
df27 = df27.filter(['P', 'u'])
df27['u'] = df27['u']/1000
df27.loc[df27['u'] == 0, 'u'] = 1
df27.to_csv('param_u.csv', index=False)

# param_o
df28 = df[(df['R'] > 0) & (df['EP'] == 1)]
df28 = df28.sort_values('K')
df28 = df28.filter(['K', 'P', 'N'])
df28.columns = ['K', 'P', 'm']
df28['o'] = 1
df28.to_csv('param_o.csv', index=False)

# param_r
df29 = df.filter(['K', 'P', 'R'])
df29.columns = ['K', 'P', 'r']
df29.to_csv('param_r.csv', index=False)

# param_q
df30 = df[df['R'] > 0]
df30 = df30.filter(['K', 'N'])
df30 = df30.reset_index(drop=True)
df30.index += 1
df30['V'] = df30.index
df30.columns = ['K', 'm', 'v']
df30['q'] = 1
df30.to_csv('param_q.csv', index=False)

# Set V
df31 = df30.filter(['v'])
df31.columns = ['V']
df31.to_csv('set_of_V.csv', index=False)

# param_Q_max
df32 = df[df['R'] > 0]
df32 = df32.filter(['K'])
df32['Q_max'] = 1000000
df32.to_csv('param_Q_max.csv', index=False)

# param_s (components having demands and only +R)
df33 = df[df['R'] < 0]
df34 = df[~df['K'].isin(df33['K'])]
df34 = df34.filter('K')
df35 = df34[df34['K'].isin(df13['K'])]
df35['s'] = 1
df35 = df35.drop_duplicates('K')
df35 = df35.sort_values('K')
df35.to_csv('param_s.csv', index=False)


