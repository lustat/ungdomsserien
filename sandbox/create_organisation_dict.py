# Create dictionary of organisation ID
import os
import pandas as pd
import json


event_files = 'C:\\Users\\Klas\\PycharmProjects\\ungdomsserien\\events_storage'


files = [filename for filename in os.listdir(event_files) if (not filename.startswith('Result_')) & (filename.endswith('csv'))]

df = pd.DataFrame()
for file in files:
    dftemp = pd.read_csv(os.path.join(event_files, file))

    if df.empty:
        df = dftemp.copy()
    else:
        df = df.append(dftemp)

dct = {}
print("dct = {")
for orgid in df.orgid.unique():
    dftemp = df.loc[df.orgid==orgid]
    club = dftemp.iloc[0].club

    region = dftemp.iloc[0].region
    print(str(orgid) + ':' + str(region) + ',')
print("}")



dct = {}
for orgid in df.orgid.unique():
    dftemp = df.loc[df.orgid==orgid]
    club = dftemp.iloc[0].club
    club = club.replace("å",'aa').replace("ä",'ae').replace("ö",'o')
    club = club.replace("æ",'ae').replace("ø",'o')
    club = club.replace("Å", 'Aa').replace("Ä", 'Ae').replace("Ö", 'O')
    club = club.replace("Æ", 'Ae').replace("Ø", 'O')

    region = dftemp.iloc[0].region
    dct[str(orgid)] = (str(region), club)

print(dct)
json = json.dumps(dct, indent=8)
f = open("../test/region.json", "w")
f.write(json)
f.close()


print('Finished')