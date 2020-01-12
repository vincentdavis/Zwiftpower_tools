import requests
import math
from zp_tools import make_collage, get_team_data, get_team_avitars, get_team_data


class create_team_collage(object):
    """
    img_path: the full path of the output image file.
    avitar_path: Folder to download and or find the avitars
    team_id: The zp team id "2740" # CRYO-GEN
    Example:
    create_team_collage(2200, 2200 , r'/Volumes/GoogleDrive/My Drive/Team CRYO-GEN/Admin/Data Science Manager/profile_img')
    """
    def __init__(self, img_path, avitar_path, team_id, update_all):
        self.img_path = img_path
        self.avitar_path = avitar_path
        self. team_id = team_id
        self.update_all = update_all
    def make(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        s = requests.Session()
        team_ids = get_team_data(self.team_id, headers=headers, s=s)
        team_size = len(team_ids['zwid'])
        image_size = math.floor(team_size**.5)*100
        print(f'Found {team_size} team members, image size wil be {image_size} square')
        get_team_avitars(team_ids['zwid'], out_path=self.avitar_path, update_all=False, headers=headers, s=s)
        make_collage(image_size, image_size , self.img_path)
