import os
from typing import Any, Union

import requests
from PIL import Image
from math import floor
from random import choice
from zp_tools_old import get_team_data, get_team_avitars, get_team_data

def team_riders_to_csv(team_id, out_file='team_riders.csv'):
    get_team_data(team_id).to_csv(out_file)

class create_team_collage(object):
    """
    img_path: the full path of the output image file.
    avitar_path: Folder to download and or find the avitars
    team_id: The zp team id "2740" # CRYO-GEN
    update_all: Suggest False unless its the first run. Get avitars for All or only those not found in the folder. Suggest False
    Example:
    create_team_collage(r'data/collage.jpeg', r'data/avitars', '2740', update_all=False)
    """
    def __init__(self, img_path, avitar_path, team_id, update_all):
        self.img_path = img_path
        self.avitar_path = avitar_path
        self. team_id = team_id
        self.update_all = update_all
        self.image_size = None

    def make_collage(self):
        '''make a collage from all images in folder'''
        listofimages = [f for f in os.listdir(self.avitar_path) if f.endswith(".jpeg")]
        cols = (len(listofimages) ** .5)
        if cols == floor(cols):
            rows = cols
        else:
            cols = floor(cols)
            rows = cols + 1
        filler_count = cols * rows - len(listofimages)
        for c in range(filler_count):
            listofimages.append(choice(listofimages))
        thumbnail_width = self.image_size // cols
        thumbnail_height = self.image_size // rows
        size = thumbnail_width, thumbnail_height
        new_im = Image.new('RGB', (self.image_size, self.image_size))
        ims = []
        for p in listofimages:
            im = Image.open(self.avitar_path + '/' + p)
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

        new_im.save(self.img_path)

    def make(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        s = requests.Session()
        team_ids = get_team_data(self.team_id, headers=headers, s=s)
        team_size = len(team_ids['zwid'])
        self.image_size = floor(team_size**.5)*100
        print(f'Found {team_size} team members, image size wil be {self.image_size} square')
        get_team_avitars(team_ids['zwid'], out_path=self.avitar_path, update_all=False, headers=headers, s=s)
        self.make_collage()

