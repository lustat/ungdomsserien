# Create dictionary of organisation ID
import os
import pandas as pd
import yaml
from definitions import DATA_DIR


event_files = f'{DATA_DIR}/02_raw_data'
files = [filename for filename in os.listdir(event_files) if filename.startswith('event_')]

dfs = []
for file in files:
    df0 = pd.read_parquet(f'{DATA_DIR}/02_raw_data/{file}')
    dfs.append(df0)
df = pd.concat(dfs, axis=0)
df = df[['orgid', 'region']].drop_duplicates()
df = df.set_index('orgid')
club_to_org = df.to_dict()['region']

with open(f"{DATA_DIR}/02_raw_data/club_to_region.yaml", "w") as file:
    yaml.dump(club_to_org, file)
print("YAML file saved.")
