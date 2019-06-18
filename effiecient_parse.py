import time
start = time.time()
import xml.etree.ElementTree as ET
import pandas


tree = ET.parse('WRDez_VA20160112_kompl_K2_y_reducedSiteMod_1.xml')
data = tree.getroot()[2]  # to get <data>, there might be a more robust way for this.

components = []  # creates an empty list
for child in data.getchildren():
    if child.tag == 'K_unit':
        for child_2 in child.getchildren():
            if child_2.tag == 'K_id':
                plants = child_2.text
            if child_2.tag == 'K_YearOpHours':
                Operation_hours = child_2.text
            elif child_2.tag == 'K_unitOpMode':
                for child_3 in child_2.getchildren():
                    if child_3.tag == 'K_name':
                        process = plants + '_' + child_3.text
                    if child_3.tag == 'K_UMYearCapacity':
                        u_capacity = child_3.text
                    elif child_3.tag == 'K_recipe':
                        for child_4 in child_3.getchildren():
                            if child_4.tag == 'K_component_proc':
                                for child_5 in child_4.getchildren():
                                    if child_5.tag == 'K_component':
                                        component = child_5.text
                                    if child_5.tag == 'K_value':
                                        r_value = child_5.text
                                    elif child_5.tag == 'K_EndProduct':
                                        end_product = child_5.text
                                        components.append({"N": plants, "Op Hours": Operation_hours, "P": process, "u": u_capacity, "K": component, "R": r_value, "EP": end_product})

pd = pandas.DataFrame(components)
pd.to_csv('components.csv')

with open('production.csv', 'w') as file1:
    with open('costs1.csv', 'w') as file2:
        for a in data.getchildren():
            if a.tag == 'K_DynamicData':
                for b in a.getchildren():
                    if b.tag == 'K_DDMarketing':
                        for c in b.getchildren():
                            if c.tag == 'K_Line':
                                production = c.text
                                file1.write(production+"\n")
                    if b.tag == 'K_DDEcoData':
                        for d in b.getchildren():
                            if d.tag == 'K_Line':
                                cost = d.text
                                file2.write(cost+"\n")

df = pandas.read_csv('production.csv', sep=';', skiprows=8, encoding='ansi', decimal=',', index_col=False)
#df = df[df['Site'] == 9876]
#df = df.groupby(['Component']).sum()
df.to_csv('demands.csv', index=False)
df1 = pandas.read_csv('costs1.csv', sep=';', skiprows=7, encoding="ansi", decimal=',')
df1.to_csv('costs2.csv')
# df2 = df1['2015'].str.replace(',', '').astype(float)
df2 = df1.groupby(['Component', 'Parameter']).sum().reset_index()
# df2.to_csv('costs3.csv')
cm = df2[df2['Parameter'] == "CM1"]
amount = df2[df2['Parameter'] == "Amount"]
specific_cm = cm.merge(amount, how='outer', on=['Sales Product', 'Component'], suffixes=['CM1', 'Amount'])
specific_cm['SpecificCM1'] = specific_cm['2015CM1'] / specific_cm['2015Amount']
specific_cm.loc[specific_cm['2015Amount'] == 0, 'SpecificCM1'] = 0
#specific_cm = specific_cm[specific_cm['Site Code'] == 50]
specific_cm.to_csv('costs.csv', index=False)
# df1 = df1.filter(['Component', 'Parameter', '2015'])
# df2 = df1[df1['2015'].replace(',', '').astype(float)]
# print(df2)
# df2 = df1[df1['Parameter'] == "Amount"]
# df2 = df2['2015'].str.replace(',', '').astype(float)
# #print(df2)
# df2.to_csv('amount_float.csv', index=False)
# df3 = df1[df1['Parameter'] == "CM1"]
# df4 = df3['2015'].str.replace(',', '').astype(float)
# df4.to_csv('cm1_float.csv', index=False)
# df5 = pandas.read_csv('amount_float.csv')
# df6 = pandas.read_csv('cm1_float.csv')
# df5 = df4/df2
# print(df5)
# df4['specific_CM1'] = df3['2015']/df2['2015']
# cm = df1[df1['Parameter'] == "CM1"]
# df2.to_csv('costs2.csv', index=False)
# df3.to_csv('costs3.csv', index=False)
# df4 = pandas.read_csv('costs.csv')
# print(df4.dtypes)
# df4['specific_CM1'] = df4['2015CM1']/df4['2015Amount']
# df4.to_csv('CM1.csv', index=False)
end = time.time()
print(end - start)





