import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
import wget
import os
import math
from PIL import Image
from random import randint
from time import sleep
import random
import json
from datetime import datetime


# A set of tools to get data from Zwift power.


class rider(object):
    """
    Represents a rider:
    Typically you what the run get_profile_details whihc completes the profile data.
    """

    def __init__(self, zwid, headers=None, s=None):
        self.zwid = zwid
        self.page_url = f"https://www.zwiftpower.com/profile.php?z={self.zwid}"
        self.data_url = f"https://www.zwiftpower.com/api3.php?do=profile_results&z={self.zwid}"
        self.page_xml = None
        self.profile = {}
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"} if headers is None else headers
        self.s = requests.Session() if s is None else s

    def __get_page_xml(self):
        self.page_xml = BeautifulSoup(self.s.get(self.page_url, headers=self.headers).content, "lxml")

    def get_profile_details(self):
        if self.page_xml is None:
            self.__get_page_xml()
        aurl = self.page_xml.find("img", {"class": "img-circle"})
        if aurl:
            self.avitar_url = self.page_xml.find("img", {"class": "img-circle"}).get("src")
        else:
            self.avitar_url = None
        self.profile['long_bio'] = self.page_xml.find(id='long_bio').text
        self.profile['zwift_level'] = self.page_xml.find(title='Zwift in-game level').text
        table = self.page_xml.find("table", id="profile_information")
        table_rows = table.find_all("tr")
        for tr in table_rows:
            td = tr.find_all(["td", "th"])
            row = [i.text.strip() for i in td]
            #print(row)
            if "Country" in row and not row[1][0].isdigit():
                self.profile["country"] = row[1] or None
            if "Race Ranking" in row:
                self.profile["race_rank_pts"] = int("".join(c for c in row[1].split(" ")[0] if c.isdigit()))
                self.profile["race_rank_place"] = int("".join(c for c in row[1].split(" pts in ")[1] if c.isdigit()))
            if "Category" in row:

                self.profile["race_rank_catagory"] = int("".join(c for c in row[1] if c.isdigit()))
            if "Age Group" in row:
                self.profile["race_rank_age"] = int("".join(c for c in row[1] if c.isdigit()))
            if "Weight Group" in row:
                self.profile["race_rank_weight"] = int("".join(c for c in row[1] if c.isdigit()))
            if "Team" in row:
                row_test = "".join(c for c in row[1] if c.isdigit())
                if row_test.isdigit():
                    self.profile["race_rank_team"] = int("".join(c for c in row[1] if c.isdigit()))
                else:
                    self.profile["race_team"] = row[1] or None
            if "Minimum Category" in row:
                self.profile["minimum_category"] = row[1][0] or None
                self.profile["minumun_catagory_female"] = row[1][2] if row[1][2] in ['A', 'B', 'C', 'D', 'E'] else None
                self.profile['races'] = int("".join(c for c in row[1] if c.isdigit()))
            if "Age" in row:
                self.profile["age"] = row[1] or None
            if "Average" in row:
                self.profile["average_watts"] = int(row[1].split("watts")[0])
                self.profile["average_wkg"] = float(row[1].split(" / ")[1].replace("wkg", ""))
            if "FTP" in row:
                self.profile["ftp"] = int(row[1].split("w")[0])
                self.profile["kg"] = int("".join(c for c in row[1].split('~ ')[1] if c.isdigit()))

    def get_data(self):
        """
        Get user data from API
        zp_id = 593408
        """
        # self.data = pd.DataFrame(self.s.get(self.data_url, headers=self.headers).json()["data"])
        self.data = self.s.get(self.data_url, headers=self.headers).json()["data"]

    def get_user_avitar(self, out_folder):
        """
        Get user avitar
        zp_id = 593408
        """
        if self.avitar_url is None:
            self.get_profile_details()
        try:
            wget.download(
                self.avitar_url,
                out=out_folder + "/zwid_" + str(self.zwid) + "_" + self.avitar_url.rsplit("/", 1)[-1] + ".jpeg",
            )
        except Exception as ex:
            print(ex)
            print(f"The url is: {self.avitar_url}")


"""
################################
Team tools
################################
"""

class Team(object):
    """
        Represents a Team:
        Typically you what the run get_profile_details whihc completes the profile data.
        """

    def __init__(self, team_id, headers=None, s=None):
        self.team_id = team_id
        self.page_url = f"https://www.zwiftpower.com/team.php?id={team_id}"
        self.data_url = f"https://www.zwiftpower.com/api3.php?do=team_riders&id={team_id}"
        self.results_url = f"https://www.zwiftpower.com/api3.php?do=team_results&id={team_id}.csv"
        self.page_xml = None
        self.results = None
        self.events = None
        self.event_results = None
        self.riders = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"} if headers is None else headers
        self.s = requests.Session() if s is None else s

    def __get_page_xml(self):
        if self.page_xml is None:
            self.page_xml = BeautifulSoup(self.s.get(self.page_url, headers=self.headers).content, "lxml")

    def __get_team_results(self):
        if self.event_results is None:
            page = self.s.get(self.results_url, headers=self.headers).json()
            self.results = page["data"]
            # self.events = page['events']
            # self.event_results = {v['zid']: {'date': v['date'], 'title': v['title']} for k, v in self.events.items()}
            self.events = {v['zid']: {'date': v['date'], 'title': v['title']} for k, v in page['events'].items()}

    def download_team_results(self, filename=None):
        """
        :param team_id: for example "2740"
        :param filename: path or defaults to team_id_date_time.csv
        :return:
        """
        filename = f"results_{self.team_id}_{datetime.now()}"
        self.__get_team_results()
        csv_columns = ['name', 'pos', 'position_in_cat', 'date', 'title' ,'DT_RowId', 'ftp', 'friend', 'pt', 'label', 'zid', 'cp', 'zwid', 'res_id', 'lag', 'uid', 'time', 'time_gun', 'gap', 'vtta', 'vttat', 'male', 'tid', 'topen', 'tname', 'tc', 'tbc', 'tbd', 'zeff', 'category', 'height', 'flag', 'avg_hr', 'max_hr', 'hrmax', 'hrm', 'weight', 'power_type', 'display_pos', 'src', 'age', 'zada', 'note', 'div', 'divw', 'skill', 'skill_b', 'skill_gain', 'np', 'hrr', 'hreff', 'avg_power', 'avg_wkg', 'wkg_ftp', 'wftp', 'wkg_guess', 'wkg1200', 'wkg300', 'wkg120', 'wkg60', 'wkg30', 'wkg15', 'wkg5', 'w1200', 'w300', 'w120', 'w60', 'w30', 'w15', 'w5', 'is_guess', 'upg', 'penalty', 'reg', 'fl', 'pts', 'pts_pos', 'info', 'info_notes', 'f_t', 'ed', 'notes']
        list_col = []
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for r in self.results:
                try:
                    r.update(self.events[r['zid']])
                    r['date'] = str(datetime.fromtimestamp(r['date']))
                except Exception as e:
                    r['date'] = "-"
                    continue # Dont write that row
                if len(list_col) == 0: # crude way to get a lit of columns to reformat
                    for k, v in r.items():
                        if isinstance(v, list):
                            list_col.append(k)
                    for lc in list_col:
                        try:
                            r[lc] = r[lc][0]
                        except:
                            pass
                else:
                    for lc in list_col:
                        try:
                            r[lc] = r[lc][0]
                        except:
                            pass
                writer.writerow(r)

    def get_team_riders(self, save_as=False):
        """
        Gets team data from API. Returns JSON as a dict
        cryo-gen team_id = 2740
        """
        team_riders = self.s.get(self.data_url, headers=self.headers).json()["data"]
        num_to_letter = {40: "D", 30: "C", 20: "B", 10: "A", 5: "A+", 0: "E"}
        for k in team_riders:
            k["div_letter"] = num_to_letter[k["div"]]
            k["divw_letter"] = num_to_letter[k["divw"]]
        self.riders = team_riders


    def get_team_avitars(team_ids, out_path="profile_img", update_all=False):
        """
        team_ids from a ppandas DF, team['zwid']
        """
        if update_all == False:  # only adds new persons
            list_of_ids = [f.lstrip("zwid_").split("_")[0] for f in os.listdir(out_path) if f.endswith(".jpeg")]
        for r in team_ids:
            if update_all == True:  # get everything again
                get_user_avitar(r, headers=headers, s=s)
                sleep(randint(0, 3))
            else:  # only get new
                if str(r) not in list_of_ids:
                    get_user_avitar(r, headers=headers, s=s)
                    sleep(1)


def get_team_list(headers=None, s=requests.Session()):
    """
    Get a list of all teams
    """
    if headers == None:
        headers = headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
    url = f"https://zwiftpower.com/api3.php?do=team_list"
    team_list = s.get(url, headers=headers)
    zp_team_list = pd.DataFrame(team_list.json()["data"])
    zp_team_list["races"] = zp_team_list["races"].replace({"": 0})
    zp_team_list["riders"] = zp_team_list["riders"].replace({"": 0})
    zp_team_list = zp_team_list.astype({"races": "int32", "riders": "int32"})
    zp_team_list.sort_values(by="riders", ascending=False, inplace=True)
    zp_team_list["races_rider_ratio"] = zp_team_list.races / zp_team_list.riders
    return zp_team_list


def get_event_list(headers=None, s=requests.Session()):
    """
    Get a list of all teams
    """
    url = f"https://zwiftpower.com/api3.php?do=zwift_event_list&_=1581097657241"
    event_list = s.get(url, headers=headers)
    zp_team_list = pd.DataFrame(event_list.json()["data"])
    zp_team_list["races"] = zp_team_list["races"].replace({"": 0})
    zp_team_list["riders"] = zp_team_list["riders"].replace({"": 0})
    zp_team_list = zp_team_list.astype({"races": "int32", "riders": "int32"})
    zp_team_list.sort_values(by="riders", ascending=False, inplace=True)
    zp_team_list["races_rider_ratio"] = zp_team_list.races / zp_team_list.riders
    return zp_team_list


"""
################################
helpers
################################
"""


def next_fileame(file_name):
    if os.path.exists(file_name):
        name, ext = file_name.rsplit(".")
        i = 0
        while os.path.exists(f"{name}_{i}.{ext}"):
            i += 1
        return f"{name}_{i}.{ext}"
    else:
        return f"{file_name}"
