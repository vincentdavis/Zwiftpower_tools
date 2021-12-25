import configparser
import datetime
from datetime import date

from requests_html import HTMLSession

from tinydb import TinyDB
from tinydb import Query

try:
    from pymongo import MongoClient
except:
    pass

class ZMongodb(object):
    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            mongoauth = config['MONGODB']['auth']
        except Exception as e:
            print('login: Need a proper config.ini file or supply auth info')
            raise e
        self.client = MongoClient(mongoauth, tlsCAFile="zwift-WTRL mongodb ca-certificate.cer")
        self.db = self.client['zwiftandmore']
        self.cached = {'results': self.db['results'], 'teams': self.db['teams'],
                       'profiles': self.db['profiles'], 'teamlist': self.db['teamlist'],
                       'live': self.db['live']}

        def check_cache(self, table, zid):
            # TODO should make sure there are not more then 1
            # TODO Get most recent.
            is_in_cache = self.cached[table].get(QID.zid == zid)
            is_in_cache = self.cached[table].find_one()
            if is_in_cache is not None:
                return is_in_cache
            else:
                return None

        def mostrecent(self, table):
            dbtable = self.cached[table]
            if dbtable.all():
                return dbtable.get(doc_id=dbtable.all()[-1].doc_id)
            else:
                return None



class ZDatabase(object):
    """
    database class needs to have:
    check_cache:
    mostrecent:
    upsert
    """
    def __init__(self, db_path='database/z_database.json'):
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.cached = {'results': self.db.table('results'), 'teams': self.db.table('teams'),
                       'profiles': self.db.table('profiles'), 'teamlist': self.db.table('teamlist'),
                       'live': self.db.table('live')}

    def check_cache(self, table, zid):
        QID = Query()
        is_in_cache = self.cached[table].get(QID.zid == zid)
        if is_in_cache is not None:
            return is_in_cache
        else:
            return None

    def mostrecent(self, table):
        dbtable = self.cached[table]
        if dbtable.all():
            return dbtable.get(doc_id=dbtable.all()[-1].doc_id)
        else:
            return None

    def upsert(self, table, data):
        QID = Query()
        self.cached[table].upsert(data, QID.zid == data['zid'])


class FetchJson(object):
    def __init__(self, login_data=None, db=ZDatabase()):
        if login_data is None:
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                self.login_data = {'username': config['LOGIN']['username'],
                                   'password': config['LOGIN']['password'],
                                   'login': 'Login'}
            except Exception as e:
                print('login_data: Need a proper config.ini file or supply login info')
                raise e
        else:
            self.login_data = login_data
        self.db = db
        self.session = None

    def login(self):
        if self.session is None:
            self.session = HTMLSession()
            z = self.session.get('https://zwiftpower.com')
            # TODO log rather then print
            # print(z.cookies.get('phpbb3_lswlk_sid'))
            self.login_data['sid'] = z.cookies.get('phpbb3_lswlk_sid')
        if "Login Required" in z.text:  # get logged in
            try:
                self.session.post("https://zwiftpower.com", data=self.login_data)
                assert "Profile" in self.session.get("https://zwiftpower.com/events.php").text
                print('Login successful')
            except Exception as e:
                # TODO log rather then print
                print(f"Failed to login: {e}")

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
                self.db.upsert("results", result)
                return result
            except Exception as e:
                # TODO log rather then print
                print(f"result error: {e}")
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
        #     # TODO log rather then print
        #     print(f"datetime.datetime.utcnow(): Live data error: {e}")
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
                self.db.upsert("teams", team)
                return team
            except Exception as e:
                # TODO log rather then print
                print(f"fetch_team error: {e}")
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
                self.db.upsert("teamlist", teamlistdata)
                return teamlistdata
            except Exception as e:
                # TODO log rather then print
                print(f"fetch_team list error: {e}")

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
                self.db.upsert("profiles", profile)
                return profile
            except Exception as e:
                # TODO log rather then print
                print(f"fetch_profile error: {e}")

    def fetch_profile2(self):
        """
        Not implemented.
        """
        # with self.session.get("https://zwiftpower.com/profile.php?z=1703891") as res:
        #     r = res
        #     return (r, self.session)
        pass
