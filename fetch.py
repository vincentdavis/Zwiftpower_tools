import configparser
import datetime
from datetime import date
from typing import Any

from bs4 import BeautifulSoup
from requests_html import HTMLSession
import logging
from ZFileDb import ZFileDb

logging.basicConfig(filename='fetcher.log', encoding='utf-8', level=logging.ERROR)

class FetchJson(object):
    def __init__(self, login_data=None, db=ZFileDb()):
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
        Fetch the results from an event (zid)
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
            return is_in_cache, 'cache'
        else:
            try:
                with self.session.get(viewurl) as res:
                    view = res.json()
                with self.session.get(zwifturl) as res:
                    zwift = res.json()
                result = {'zid': zid, 'timestamp': tstamp, 'view_data': view['data'], 'zwift_data': zwift['data']}
                self.db.upsert('results', result)
                return result, 'refresh'
            except Exception as e:
                logging.error(f"Fetch Result Error: {e}")

    def event_list(self, refresh=False):
        """
        Search for upcoming events.
        """
        event_list_url = "https://zwiftpower.com/cache3/lists/0_zwift_event_list_3.json"

    def result_list(self, refresh=False):
        """
        Search recent event list
        """
        result_list_url = "https://zwiftpower.com/cache3/lists/0_zwift_event_list_results_3.json?_=1641522900935"
        tstamp = datetime.datetime.utcnow().isoformat()
        zid = datetime.datetime.utcnow().strftime('%Y-%m-%d-%Hhr')
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('results_list', zid)
        if is_in_cache:
            return is_in_cache, 'cache'
        else:
            try:
                with self.session.get(result_list_url) as res:
                    results_list = res.json()
                    results_list: dict[str, Any] = {'zid': zid, 'tstamp': tstamp, 'results_list': results_list['data']}
                    self.db.upsert('results_list', results_list)
                return results_list, 'refresh'
            except Exception as e:
                logging.info(f"result_list error: {e}")
                return None, None

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
            is_in_cache = self.db.check_cache('teams', zid)
        if is_in_cache:
            return is_in_cache, 'cache'
        else:
            try:
                with self.session.get(teamurl) as res:
                    teamdata = res.json()
                    team: dict[str, Any] = {'zid': zid, 'tstamp': tstamp, 'team': teamdata['data']}
                    self.db.upsert('teams', team)
                return team, 'refresh'
            except Exception as e:
                logging.info(f"fetch_ateam error: {e}")
                return None

    def fetch_teamlist(self, refresh=False):
        """
        We use today's date as zid for upsert.
        Gets the list of ZwiftPower teams
        """
        # teamlistownurl = "https://zwiftpower.com/api3.php?do=team_list_own"
        teamlisturl = "https://zwiftpower.com/api3.php?do=team_list"
        tstamp = datetime.datetime.utcnow().isoformat()
        day = date.today().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.mostrecent('teamlist')
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(teamlisturl) as res:
                    teamlistsdata = res.json()
                    teamlistsdata = {'zid': f"teamlist_{tstamp}", 'tstamp': tstamp, 'teamlist': teamlistsdata['data']}
                self.db.upsert('teamlist', teamlistsdata)
                return teamlistsdata
            except Exception as e:
                logging.error(f"fetch_teamlist error: {e}")

    def fetch_profile(self, zid, profile_ext = True, refresh=False):
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
                    pall = pall['data']
            except Exception as e:
                pall = None
                logging.error(f"fetch_profile error, allurl: {e}")
            try:
                with self.session.get(victimsurl) as res:
                    victim = res.json()
                    victim = victim['data']
            except Exception as e:
                victim = None
                logging.error(f"fetch_profile error, victimsurl: {e}\n**{victimsurl}")
            try:
                with self.session.get(analysisurl) as res:
                    analysis = res.json()
                    analysis = analysis['data']
            except Exception as e:
                analysis = None
                logging.error(f"fetch_profile error, analysisurl: {e}")
            if profile_ext:
                try:
                    profile_ext_data = self.fetch_profile_ext(zwid = zid)
                except Exception as e:
                    profile_ext_data = None
                    logging.error(f"fetch_profile error, profile_ext_data: {e}")
            try:
                profile = {'zid': zid, 'tstamp': tstamp, 'pall': pall, 'victim': victim,
                           'analysis': analysis, 'profile_ext': profile_ext_data}
                self.db.upsert('profiles', profile)
                return profile
            except Exception as e:
                logging.error(f"fetch_profile error, upsert: {e}")

    def fetch_profile_ext(self, zwid, refresh=False, avatar=True):
        """
        Avatar should be false or a path "database/avatar/"
        """
        page_url = f"https://zwiftpower.com/profile.php?z={zwid}"
        page_xml = BeautifulSoup(self.session.get(page_url).content, "lxml")
        profile_ext = {}
        try:
            aurl = page_xml.find("img", {"class": "img-circle"})
            if aurl:
                profile_ext['avatar_url'] = page_xml.find("img", {"class": "img-circle"}).get("src")
            else:
                profile_ext['avatar_url'] = None
            profile_ext['long_bio'] = page_xml.find(id='long_bio').text if page_xml.find(
                id='long_bio') else None
            profile_ext['zwift_level'] = page_xml.find(
                title='Zwift in-game level').text if page_xml.find(title='Zwift in-game level') else None
            table = page_xml.find("table", id="profile_information")
            if table:
                table_rows = table.find_all("tr")
                for tr in table_rows:
                    td = tr.find_all(["td", "th"])
                    row = [i.text.strip() for i in td]
                    # print(row)
                    if "Country" in row and not row[1][0].isdigit():
                        profile_ext["country"] = row[1] or None
                    if "Race Ranking" in row:
                        profile_ext["race_rank_pts"] = int("".join(c for c in row[1].split(" ")[0] if c.isdigit()))
                        profile_ext["race_rank_place"] = int(
                            "".join(c for c in row[1].split(" pts in ")[1] if c.isdigit()))
                    if "Category" in row:
                        profile_ext["race_rank_catagory"] = int("".join(c for c in row[1] if c.isdigit()))
                    if "Age Group" in row:
                        profile_ext["race_rank_age"] = int("".join(c for c in row[1] if c.isdigit()))
                    if "Weight Group" in row:
                        profile_ext["race_rank_weight"] = int("".join(c for c in row[1] if c.isdigit()))
                    if "Team" in row:
                        row_test = "".join(c for c in row[1] if c.isdigit())
                        if row_test.isdigit():
                            profile_ext["race_rank_team"] = int("".join(c for c in row[1] if c.isdigit()))
                        else:
                            profile_ext["race_team"] = row[1] or None
                    if "Minimum Category" in row:
                        profile_ext["minimum_category"] = row[1][0] or None
                        profile_ext["minumun_catagory_female"] = row[1][2] if row[1][2] in ['A', 'B', 'C', 'D',
                                                                                        'E'] else None
                        profile_ext['races'] = int("".join(c for c in row[1] if c.isdigit()))
                    if "Age" in row:
                        profile_ext["age"] = row[1] or None
                    if "Average" in row:
                        profile_ext["average_watts"] = int(row[1].split("watts")[0])
                        profile_ext["average_wkg"] = float(row[1].split(" /")[1].replace("wkg", ""))
                    if "FTP" in row:
                        profile_ext["ftp"] = None
                        profile_ext["kg"] = None
                        try:
                            profile_ext["ftp"] = int(row[1].split("w")[0])
                            profile_ext["kg"] = int("".join(c for c in row[1].split('~ ')[1] if c.isdigit()))
                        except Exception as e:
                            logging.error(f"FTP not found: {e}")
        except Exception as e:
            logging.error(f"fetch_profile_ext error: {e}")
        try:
            if avatar:
                # database/avatar/
                try:
                    tstamp = datetime.datetime.utcnow().isoformat()
                    file_name = f"avatar_{zwid}_{tstamp}.jpeg"
                    avatar_file = self.session.get(profile_ext['avatar_url'])
                    self.db.save_avatar(file_name, avatar_file)
                except Exception as e:
                    logging.error(f"Avatar file save error: {e}")
                    avatar_file = None
                finally:
                    profile_ext['avatar_file'] = file_name
        except Exception as e:
            profile_ext['avatar_file'] = None
            logging.error(f"fetch_profile_ext AVattar error: {e}")
        finally:
            return profile_ext

    def fetch_sprints(self, zid, refresh=False):
        """
        Fastest through segment: FTS
        """
        ftsurl = f"https://zwiftpower.com/api3.php?do=event_sprints&zid={zid}"
        tstamp = datetime.datetime.utcnow().isoformat()
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('event_fts', zid)
        if is_in_cache:
            return is_in_cache, 'cache'
        else:
            try:
                with self.session.get(ftsurl) as res:
                    ftsdata = res.json()
                fts = {'zid': zid, 'tstamp': tstamp, 'fts': ftsdata['data']}
                self.db.upsert('event_fts', fts)
                return fts, 'refresh'
            except Exception as e:
                logging.info(f"fetch_sprints FTS error: {e}")
                print(e)
                return None, 'refresh'

class Fetch_WTRL(object):
    """
    For getting data from WTRL
    """
    def __init__(self, login_data=None, db=ZFileDb()):
        if login_data is None:
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                self.login_data = config['WTRL']['auth']
            except Exception as e:
                logging.warning('login_data: Need a proper config.ini file or supply login info')
                raise e
        else:
            self.login_data = login_data
        self.db = db
        self.session = HTMLSession() # s = requests_html.session():
        try:
            r = self.session.get('https://www.wtrl.racing')
            assert r.status_code == 200
            self.session.headers.update({"Authorization": self.login_data,  # static for ur account
                              "Content-Type": "application/x-www-form-urlencoded"})
        except:
            logging.error(f"https://www.wtrl.racing returned status code: {r.status_code}")

    def fetch_ttt(self, zid, refresh=False):
        """
        Fetch Team Time Trial results
        zid = the ttt number
        """
        ttturl="https://www.wtrl.racing/api/wtrlruby.php"
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('wtrl_ttt', zid)
        if is_in_cache:
            return is_in_cache, 'cache'
        else:
            try:
                data = {
                    "wtrlid": "wtrlttt",
                    "season": zid,  # session
                    "action": "results"}
                with self.session.post(ttturl, data=data) as res:
                    ttt_json = res.json()
                ttt_result = {'zid': zid, 'ttt_json': ttt_json}
                self.db.upsert('ttt_result', ttt_result)
                return ttt_result, 'refresh'
            except Exception as e:
                logging.error(f"Failed to fetch and save ttt result: {e}")


