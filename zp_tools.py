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

# A set of tools to get data from Zwift power.

def get_team_page(team_id, headers=None, s=requests.Session()):
    '''
    Gets full team page content.
    cryo-gen team_id = 2740
    '''
    url = f'https://www.zwiftpower.com/team.php?id={team_id}'
    return BeautifulSoup(s.get(zpteam_url, headers=headers).content, 'html.parser')


def get_team_data(team_id, header=None, s=requests.Session()):
    '''
    Gets team data from API. Returns dataframe
    cryo-gen team_id = 2740
    '''
    url = f'https://www.zwiftpower.com/api3.php?do=team_riders&id={team_id}'
    zp_team_api = s.get(zp_api, headers=headers)
    return pd.DataFrame(s.get(zp_api, headers=headers).json()['data'])


def get_user_page(zp_id, header=None, s=requests.Session()):
    '''
    Get the user profile page
    zp_id = 593408
    '''
    url = f'https://www.zwiftpower.com/profile.php?z={zp_id}'
    return BeautifulSoup(s.get(url, headers=headers).content, 'html.parser')


def get_user_data(zp_id, header=None, s=requests.Session()):
    '''
    Get user data from API
    zp_id = 593408
    '''
    url = f'https://www.zwiftpower.com/api3.php?do=profile_results&z={zp_id}'
    return pd.DataFrame(s.get(url, headers=headers).json()['data'])


def get_user_avitar(zp_id, header=None, s=requests.Session()):
    '''
    Get user avitar
    zp_id = 593408
    '''
    rx = r"https:\/\/static-cdn\.zwift\.com\/prod\/profile\/[a-z0-9]{8}-[0-9]{3,7}"
    try:
        img_url = re.search(rx, str(get_user_page(zp_id, s=s))).group(0)
        wget.download(img_url, out='profile_img/zwid_' + str(zp_id) + '_' + img_url.rsplit('/', 1)[-1] + '.jpeg')
    except Exception as ex:
        print(ex)
        print(f'https://www.zwiftpower.com/profile.php?z={zp_id}')


def get_team_results_data(team_id, header=None, s=requests.Session()):
    '''
    team_id: 240
    https://www.zwiftpower.com/api3.php?do=team_results&id=2740&_=1578282315864
    '''
    url = f'https://www.zwiftpower.com/api3.php?do=team_results&id={team_id}'
    return pd.DataFrame(s.get(url, headers=headers).json()['data'])


def get_team_avitars(team_ids):
    '''
    team_ids from a ppandas DF, team['zwid']
    '''
    # TODO, check if we have it already, have update all/new
    for r in team_ids:
        get_user_avitar(r, header=headers, s=s)
    sleep(randint(0, 3))  # just to be nice to ZP


def create_team_collage(width, height, folder):
    '''make a collage from all images in folder'''
    listofimages = [f for f in os.listdir(folder) if f.endswith(".jpeg")]
    cols = (len(listofimages) ** .5)
    if cols == math.floor(cols):
        rows = cols
    else:
        cols = math.floor(cols)
        rows = cols + 1
    thumbnail_width = width // cols
    thumbnail_height = height // rows
    size = thumbnail_width, thumbnail_height
    new_im = Image.new('RGB', (width, height))
    ims = []
    for p in listofimages:
        im = Image.open('profile_img/' + p)
        im.thumbnail(size)
        ims.append(im)
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            print(i, x, y)
            try:
                new_im.paste(ims[i], (x, y))
                i += 1
                y += thumbnail_height
            except:
                continue
        x += thumbnail_width
        y = 0

    new_im.save("Collage.jpg")