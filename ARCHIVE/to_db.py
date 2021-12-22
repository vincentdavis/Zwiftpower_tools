import requests
import pandas as pd
import datetime
from zp_tools import *
from database import *


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
s=requests.Session()
zp_team_list = get_team_list(headers=headers, s=requests.Session())
zp_team_list.fetchdatetime = datetime.datetime.now

print(zp_team_list.count())
try:
    sqlite_db.connect()
except:
    pass
for k, row in zp_team_list.iterrows():
    try:
        Teams.insert(row.to_dict()).execute()
    except Exception as e:
        print(row)
        print(e)
sqlite_db.close()

