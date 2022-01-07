from fetch import FetchJson
# Define the database
z = FetchJson()
z.login()



result = z.fetch_result(zid=2552316)
print(f"Event ID, 'zid' is: {result['zid']}")
print(f"Top level data in JSON: {result.keys()}")
print("Top five")
for racer in result['zwift_data'][:5]:
    if int(racer['pos']) <=5:
        print(f"{racer['pos']}: {racer['name']} with a time of {racer['race_time'][0]}")

import pandas as pd
df = pd.DataFrame(result['zwift_data'])

def splitlist(df, col, drop2=True):
    df[[f'{col}', f'{col}_2' ]] = df[col].tolist()
    if drop2:
        df.drop(f'{col}_2', axis=1, inplace=True)

splitlist(df, 'watts')
splitlist(df, 'wkg')
splitlist(df, 'wkg_ftp')

df.head()

df[['watts', 'wkg', 'wkg_ftp']] = df[['watts', 'wkg', 'wkg_ftp']].astype(float)
print("Plot")
df[['wkg', 'wkg_ftp']].plot()