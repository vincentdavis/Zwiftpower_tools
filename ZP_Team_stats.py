import requests
from zp_tools import get_team_data

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
s = requests.Session()


get_team_data(team_id, headers=headers, s=requests.Session()):
