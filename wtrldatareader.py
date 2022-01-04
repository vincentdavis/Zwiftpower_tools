from configparser import ConfigParser

import requests_html

config = ConfigParser()
config.read('config.ini')



s = requests_html.session()
r = s.get('https://www.wtrl.racing')
print(r.status_code)
# r = s.post(url="https://www.wtrl.racing/api/wtrlruby.php",
#                   data={
#                       "wtrlid": "wtrlttt",
#                       "season": "140", # session
#                       "action": "results"
#                   },
#                   headers= {
#                       "Authorization": config['WTRL']['auth'], # static for ur account
#                       "Content-Type": "application/x-www-form-urlencoded"
#                   })
# print(r.status_code)


