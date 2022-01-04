import configparser
import datetime
from datetime import date
from typing import Any

from bs4 import BeautifulSoup
from requests_html import HTMLSession
import logging
from ZMongodb import ZMongodb


class FetchJson(object):
    def __init__(self, login_data=None, db=ZMongodb()):
        if login_data is None:
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                self.login_data = {'username': config['LOGIN']['username'],
                                   'password': config['LOGIN']['password'],
                                   'login': 'Login'}
            except Exception as e:
                logging.info('login_data: Need a proper config.ini file or supply login info')
                raise e
        else:
            self.login_data = login_data
        self.db = db
        self.session = None

    def login(self):
        if self.session is None:
            self.session = HTMLSession()
            z = self.session.get('https://zwiftpower.com')
            logging.info(z.cookies.get('phpbb3_lswlk_sid'))
            self.login_data['sid'] = z.cookies.get('phpbb3_lswlk_sid')
        if "Login Required" in z.text:  # get logged in
            try:
                self.session.post("https://zwiftpower.com", data=self.login_data)
                assert "Profile" in self.session.get("https://zwiftpower.com/events.php").text
                logging.info('Login successful')
            except Exception as e:
                logging.error(f"Failed to login: {e}")

    def fetch_result(self, zid, refresh=False):
        """
        Fetch the results from and event (zid)
        Contains:
        - view api
        - zwift api
        - event id is added as zid

        """
        viewurl = f"https://zwiftpower.com/cache3/results/{zid}_view.json"
        zwifturl = f"https://zwiftpower.com/cache3/results/{zid}_zwift.json"
        tstamp = datetime.datetime.utcnow().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('results', zid)
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(viewurl) as res:
                    view = res.json()
                with self.session.get(zwifturl) as res:
                    zwift = res.json()
                result = {'zid': zid, 'timestamp': tstamp, 'view_data': view['data'], 'zwift_data': zwift['data']}
                self.db.collection.insert_one(result)
                return result
            except Exception as e:
                logging.error(f"Fetch Result Error: {e}")

    def fetch_live_results(self, zid):
        """
        work in progress
        this is the api for the live event data.
        """
        # liveurl = f"https://zwiftpower.com/cache3/live/results_{zid}.json"
        # try:
        #     res = self.session.get(liveurl)
        #     live_data = res.json()
        #     live = {'zid': zid, 'live_data': live_data['data']}
        #     return res, live
        #     # self.db.upsert("results", result)
        #     # return result
        # except Exception as e:
        #     logging.error(f"datetime.datetime.utcnow(): Live data error: {e}")
        pass

    def fetch_team(self, zid, refresh=False):
        """
        This is the api for the rider list and data for one team.
        """
        teamurl = f"https://zwiftpower.com/api3.php?do=team_riders&id={zid}"
        tstamp = datetime.datetime.utcnow().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('profiles', zid)
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(teamurl) as res:
                    teamdata = res.json()
                    team: dict[str, Any] = {'zid': zid, 'tstamp': tstamp, 'team': teamdata['data']}
                self.db.collection.insert_one(team)
                return team
            except Exception as e:
                logging.info(f"fetch_team error: {e}")
                return None

    def fetch_teamriders(self, refresh=False):
        """
        We use today's date as zid for upsert.
        Gets the list of ZwiftPower teams
        """
        # teamlistownurl = "https://zwiftpower.com/api3.php?do=team_list_own"
        teamridersurl = "https://zwiftpower.com/api3.php?do=team_list"
        tstamp = datetime.datetime.utcnow().isoformat()
        day = date.today().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.mostrecent('teamlist')
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(teamridersurl) as res:
                    teamridersdata = res.json()
                    teamridersdata = {'zid': day, 'tstamp': tstamp, 'teamlist': teamridersdata['data']}
                # self.db.collection.insert_one(teamridersdata)
                return teamridersdata
            except Exception as e:
                logging.error(f"fetch_team list error: {e}")

    def fetch_profile(self, zid, refresh=False):
        """
        User/Rider/Profile
        """
        allurl = f"https://zwiftpower.com/cache3/profile/{zid}_all.json"
        victimsurl = f"https://zwiftpower.com/cache3/profile/{zid}_rider_compare_victims.json"
        analysisurl = f"https://zwiftpower.com/cache3/profile/{zid}_analysis_list.json"
        tstamp = datetime.datetime.utcnow().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('profiles', zid)
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(allurl) as res:
                    pall = res.json()
                with self.session.get(victimsurl) as res:
                    victim = res.json()
                with self.session.get(analysisurl) as res:
                    analysis = res.json()
                profile = {'zid': zid, 'tstamp': tstamp, 'pall': pall['data'], 'victim': victim['data'],
                           'analysis': analysis['data']}
                self.db.collection.insert_one(profile)
                return profile
            except Exception as e:
                logging.error(f"fetch_profile error: {e}")

    def fetch_profile2(self, zwid, refresh=False, avatar=False):
        """
        Avatar should be false or a path "database/avatar/"
        """
        page_url = f"https://zwiftpower.com/profile.php?z={zwid}"
        page_xml = BeautifulSoup(self.session.get(page_url).content, "lxml")
        profile = {}
        aurl = page_xml.find("img", {"class": "img-circle"})
        if aurl:
            profile['avatar_url'] = page_xml.find("img", {"class": "img-circle"}).get("src")
        else:
            profile['avatar_url'] = None
        profile['long_bio'] = page_xml.find(id='long_bio').text if page_xml.find(
            id='long_bio') else None
        profile['zwift_level'] = page_xml.find(
            title='Zwift in-game level').text if page_xml.find(title='Zwift in-game level') else None
        table = page_xml.find("table", id="profile_information")
        if table:
            table_rows = table.find_all("tr")
            for tr in table_rows:
                td = tr.find_all(["td", "th"])
                row = [i.text.strip() for i in td]
                # print(row)
                if "Country" in row and not row[1][0].isdigit():
                    profile["country"] = row[1] or None
                if "Race Ranking" in row:
                    profile["race_rank_pts"] = int("".join(c for c in row[1].split(" ")[0] if c.isdigit()))
                    profile["race_rank_place"] = int(
                        "".join(c for c in row[1].split(" pts in ")[1] if c.isdigit()))
                if "Category" in row:
                    profile["race_rank_catagory"] = int("".join(c for c in row[1] if c.isdigit()))
                if "Age Group" in row:
                    profile["race_rank_age"] = int("".join(c for c in row[1] if c.isdigit()))
                if "Weight Group" in row:
                    profile["race_rank_weight"] = int("".join(c for c in row[1] if c.isdigit()))
                if "Team" in row:
                    row_test = "".join(c for c in row[1] if c.isdigit())
                    if row_test.isdigit():
                        profile["race_rank_team"] = int("".join(c for c in row[1] if c.isdigit()))
                    else:
                        profile["race_team"] = row[1] or None
                if "Minimum Category" in row:
                    profile["minimum_category"] = row[1][0] or None
                    profile["minumun_catagory_female"] = row[1][2] if row[1][2] in ['A', 'B', 'C', 'D',
                                                                                    'E'] else None
                    profile['races'] = int("".join(c for c in row[1] if c.isdigit()))
                if "Age" in row:
                    profile["age"] = row[1] or None
                if "Average" in row:
                    profile["average_watts"] = int(row[1].split("watts")[0])
                    profile["average_wkg"] = float(row[1].split(" /")[1].replace("wkg", ""))
                if "FTP" in row:
                    profile["ftp"] = None
                    profile["kg"] = None
                    try:
                        profile["ftp"] = int(row[1].split("w")[0])
                        profile["kg"] = int("".join(c for c in row[1].split('~ ')[1] if c.isdigit()))
                    except Exception as e:
                        logging.error(f"FTP not found: {e}")

            if avatar:
                # database/avatar/
                try:
                    tstamp = datetime.datetime.utcnow().isoformat()
                    file_path = f"{avatar}{zwid}_{tstamp}.jpeg"
                    avatar_file = self.session.get(profile['avatar_url'])
                    with open(file_path, 'wb') as local_file:
                        local_file.write(avatar_file.content)
                except Exception as e:
                    logging.error(f"Avatar file save error: {e}")
                    avatar_file = None
                finally:
                    profile['avatar_file'] = avatar_file
        return profile
