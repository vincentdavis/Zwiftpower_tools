import configparser
import datetime
from datetime import date

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
                    teamlistdata = res.json()
                    teamlistdata = {'zid': day, 'tstamp': tstamp, 'teamlist': teamlistdata['data']}
                self.db.collection.insert_one(teamlistdata)
                return teamlistdata
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
                profile = {'zid': zid, 'tstamp': tstamp, 'pall': pall['data'], 'victim': victim['data'], 'analysis': analysis['data']}
                self.db.collection.insert_one(profile)
                return profile
            except Exception as e:
                logging.error(f"fetch_profile error: {e}")

    def fetch_profile2(self):
        """
        Not implemented.
        """
        # with self.session.get("https://zwiftpower.com/profile.php?z=1703891") as res:
        #     r = res
        #     return (r, self.session)
        pass
