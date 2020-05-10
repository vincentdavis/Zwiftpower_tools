import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import wget
import os
import math
from PIL import Image
from random import randint
from time import sleep
import random


# A set of tools to get data from Zwift power.

"""
################################
Individual tools
################################
"""

def get_user_page(zp_id, headers=None, s=requests.Session()):
    '''
    Get the user profile page
    zp_id = 593408
    '''
    url = f'https://www.zwiftpower.com/profile.php?z={zp_id}'
    return BeautifulSoup(s.get(url, headers=headers).content, 'html.parser')


def get_user_data(zp_id, headers=None, s=requests.Session()):
    '''
    Get user data from API
    zp_id = 593408
    '''
    url = f'https://www.zwiftpower.com/api3.php?do=profile_results&z={zp_id}'
    return pd.DataFrame(s.get(url, headers=headers).json()['data'])


def get_user_avitar(zp_id, out_folder='profile_img', headers=None, s=requests.Session()):
    '''
    Get user avitar
    zp_id = 593408
    '''
    rx = r"https:\/\/static-cdn\.zwift\.com\/prod\/profile\/[a-z0-9]{8}-[0-9]{3,7}"
    try:
        img_url = re.search(rx, str(get_user_page(zp_id, s=s))).group(0)
        wget.download(img_url, out=out_folder+'/zwid_' + str(zp_id) + '_' + img_url.rsplit('/', 1)[-1] + '.jpeg')
    except Exception as ex:
        print(ex)
        print(f'https://www.zwiftpower.com/profile.php?z={zp_id}')

"""
################################
Team tools
################################
"""

def get_team_page(team_id, headers=None, s=requests.Session()):
    '''
    Gets full team page content.
    cryo-gen team_id = 2740
    '''
    if headers == None:
        headers = headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    url = f'https://www.zwiftpower.com/team.php?id={team_id}'
    return BeautifulSoup(s.get(url, headers=headers).content, 'html.parser')


def get_team_data(team_id, headers=None, s=requests.Session()):
    '''
    Gets team data from API. Returns dataframe
    cryo-gen team_id = 2740

    '''
    url = f'https://www.zwiftpower.com/api3.php?do=team_riders&id={team_id}'
    team_data = s.get(url, headers=headers)
    if team_data.status_code != 200:
      return None
      # return [{'status': team_data.status_code},]
    else:
        team = pd.DataFrame(team_data.json()['data'])
        team['URL'] = 'https://www.zwiftpower.com/profile.php?z=' + str(team.zwid)
        team.sort_values(by=['div', 'divw'], ascending=False, inplace=True)
        team['div_letter'] = team_selected['div'].replace({40:'D', 30:'C', 20:'B', 10:'A',  5:'A+',  0:'Z'})
        team['divw_letter'] = team_selected['divw'].replace({40:'D', 30:'C', 20:'B', 10:'A',  5:'A+',  0:'Z'})
        return team

def get_team_results_data(team_id, headers=None, s=requests.Session()):
    '''
    team_id: 240
    https://www.zwiftpower.com/api3.php?do=team_results&id=2740&_=1578282315864
    '''
    url = f'https://www.zwiftpower.com/api3.php?do=team_results&id={team_id}'
    return pd.DataFrame(s.get(url, headers=headers).json()['data'])

def get_team_avitars(team_ids, out_path='profile_img', update_all=False, headers=None, s=requests.Session()):
    '''
    team_ids from a ppandas DF, team['zwid']
    '''
    if update_all==False: #only adds new persons
        list_of_ids = [f.lstrip('zwid_').split('_')[0] for f in os.listdir(out_path) if f.endswith(".jpeg")]
    for r in team_ids:
        if update_all == True: # get everything again
            get_user_avitar(r, headers=headers, s=s)
            sleep(randint(0, 3))
        else: # only get new
            if str(r) not in list_of_ids:
                get_user_avitar(r, headers=headers, s=s)
                sleep(1)

def get_team_list(headers=None, s=requests.Session()):
    '''
    Get a list of all teams
    '''
    url = f'https://zwiftpower.com/api3.php?do=team_list'
    team_list = s.get(url, headers=headers)
    zp_team_list = pd.DataFrame(team_list.json()['data'])
    zp_team_list['races'] = zp_team_list['races'].replace({'': 0})
    zp_team_list['riders'] = zp_team_list['riders'].replace({'': 0})
    zp_team_list = zp_team_list.astype({'races': 'int32', 'riders': 'int32'})
    zp_team_list.sort_values(by='riders', ascending=False, inplace=True)
    zp_team_list['races_rider_ratio'] = zp_team_list.races / zp_team_list.riders
    return zp_team_list

def get_event_list(headers=None, s=requests.Session()):
    '''
    Get a list of all teams
    '''
    url = f'https://zwiftpower.com/api3.php?do=zwift_event_list&_=1581097657241'
    event_list = s.get(url, headers=headers)
    zp_team_list = pd.DataFrame(team_list.json()['data'])
    zp_team_list['races'] = zp_team_list['races'].replace({'': 0})
    zp_team_list['riders'] = zp_team_list['riders'].replace({'': 0})
    zp_team_list = zp_team_list.astype({'races': 'int32', 'riders': 'int32'})
    zp_team_list.sort_values(by='riders', ascending=False, inplace=True)
    zp_team_list['races_rider_ratio'] = zp_team_list.races / zp_team_list.riders
    return zp_team_list