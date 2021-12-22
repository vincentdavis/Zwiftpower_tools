import configparser
from requests_html import HTMLSession

from tinydb import TinyDB
from tinydb import Query

class zdatabase(object):
    def __init__(self, db_path='z_database.json'):
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.cached = {'results': self.db.table('results'), 'teams': self.db.table('teams'),
                       'profiles': self.db.table('profiles')}
    def check_cache(self, table, zid):
        QID = Query()
        is_in_cache = self.cached[table].get(QID.zid == zid)
        if is_in_cache is not None:
            return is_in_cache
        else:
            return None
    def upsert(self, table, data):
        QID = Query()
        self.cached[table].upsert(data, QID.zid == data['zid'])


class fetch_json(object):
    def __init__(self, login_data=None, db=zdatabase()):
        if login_data is None:
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                self.login_data = {'username': config['LOGIN']['username'],
                                   'password': config['LOGIN']['password'],
                                   'login': 'Login'}
            except:
                print('Need a proper config.ini file or supplu login info')
        else:
            self.login_data = login_data
        self.db = db
        self.session = None

    def login(self):
        if self.session == None:
            self.session = HTMLSession()
            z = self.session.get('https://zwiftpower.com')
            print(z.cookies.get('phpbb3_lswlk_sid'))
            self.login_data['sid'] = z.cookies.get('phpbb3_lswlk_sid')
        if "Login Required" in z.text: # get logged in
            self.session.post("https://zwiftpower.com", data=self.login_data)
            assert "Profile" in self.session.get("https://zwiftpower.com/events.php").text

    def fetch_result(self, zid, refresh=False):
        viewurl = f"https://zwiftpower.com/cache3/results/{zid}_view.json"
        zwifturl = f"https://zwiftpower.com/cache3/results/{zid}_zwift.json"
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
                result = {'zid': zid, 'view_data': view['data'], 'zwift_data': zwift['data']}
                self.db.upsert("results", result)
                return result
            except Exception as e:
                print(f"fetch_result error: {e}")


    def fetch_team(self, zid, refresh=False):
        teamurl = f"https://zwiftpower.com/api3.php?do=team_riders&id={zid}"
        is_in_cache = False
        if not refresh:
            is_in_cache = self.db.check_cache('profiles', zid)
        if is_in_cache:
            return is_in_cache
        else:
            try:
                with self.session.get(teamurl) as res:
                    teamdata = res.json()
                    team = {'zid':zid, 'team': teamdata['data']}
                self.db.upsert("teams", team)
                return team
            except Exception as e:
                print(f"fetch_team error: {e}")
            return team

    def fetch_profile(self, zid, refresh=False):
        allurl = f"https://zwiftpower.com/cache3/profile/{zid}_all.json"
        victimsurl = f"https://zwiftpower.com/cache3/profile/{zid}_rider_compare_victims.json"
        analysisurl = f"https://zwiftpower.com/cache3/profile/{zid}_analysis_list.json"
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
                profile = {'zid': zid, 'pall': pall['data'], 'victim': victim['data'], 'analysis': analysis['data']}
                self.db.upsert("profiles", profile)
                return profile
            except Exception as e:
                print(f"fetch_profile error: {e}")
    def fetch_profile2(self):
        with self.session.get("https://zwiftpower.com/profile.php?z=1703891") as res:
            r = res
            return (r, self.session)













