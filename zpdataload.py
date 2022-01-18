from fetch import FetchJson
# Define the database
z = FetchJson()
z.login()


################
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

############################
tl = z.fetch_teamlist()
for t in tl['teamlist']:
    if t['tln'] == 'THE XXXX':
        team_id = t['team_id']
        # print(f"Team found:\n{t}")
triders, status = z.fetch_team(zid = team_id)
count = 0
for r in triders['team']:
    # print(r)
    p = z.fetch_profile(r['zwid'], profile_ext=True)
    # print(f"Riders count: {count}")
    count += 1
    if p is not None:
        # print(f"Rider id:{p['zid']}")
        pass
    else:
        print(f"None from rider id: {r['zwid']}")
        break
    sleep(.1)

############################
import pandas as pd
def splitlist(df, col, drop2=True):
        df[[f'{col}', f'{col}_2' ]] = df[col].tolist()
        if drop2:
            df.drop(f'{col}_2', axis=1, inplace=True)

def weight_stats(zid):
    stats = {}
    try:
        profile = z.fetch_profile(zid, profile_ext=True)['pall']
        dz = pd.DataFrame(profile)
        splitlist(dz, 'weight')
        dz = dz[dz.event_date >= 1609484400]
        dz.sort_values('event_date')
        stats['zid'] = zid
        stats['start21'] = float(dz.weight.iloc[0])
        stats['now'] = float(dz.weight.iloc[-1])
        stats['max'] = float(dz.weight.max())
        stats['min'] = float(dz.weight.min())
        stats['count'] = float(dz.weight.nunique())
        stats['mid_point'] = (stats['max'] + stats['min'])/2
        stats['scaled_max'] = stats['max']/stats['mid_point']
        stats['scaled_min'] = stats['min']/stats['mid_point']
        stats['scaled_now'] = stats['now']/stats['mid_point']
        stats["name"] = dz['name'].iloc[0]
        stats['url'] = f"https://zwiftpower.com/profile.php?z={zid}"
        return stats, None
    except:
        print(zid)
        return None, zid


team_weight_stats = []
bad_list = []
for r in triders['team']:
    # print(r)
    stat, bad = weight_stats(r['zwid'])
    if stat:
        team_weight_stats.append(stat)
    elif bad:
        bad_list.append({'zid': bad, 'url':f"https://zwiftpower.com/profile.php?z={bad}"})

team_weight_stats_pd = pd.DataFrame(team_weight_stats)
team_weight_stats_pd.to_excel('team_weight_stats.xlsx')
bad_list_pd = pd.DataFrame(bad_list)
bad_list_pd.to_excel('bad_list_2.xlsx')