from requests_html import HTMLSession
import getpass
import pandas as pd

username =  "ahussa3"
password = ".B7tCr58KgwFr%q"

# u = getpass.getpass(prompt="User")
# p = getpass.getpass(prompt="Pass")
login_data = {'username': username, 'password': password, 'login': 'Login'}

class fetch_json(object):
    def __init__(self, login_data):
        self.login_data = login_data
        self.session = None
        self.cached = {}

    def login(self):
        if self.session == None:
            self.session = HTMLSession()
            z = self.session.get('https://zwiftpower.com')
            if "Login Required" in z.text: # get logged in
                self.session.post("https://zwiftpower.com", data=login_data)

    def fetch_result(self, zid, refresh=False):
        viewurl = f"https://zwiftpower.com/cache3/results/{zid}_view.json"
        zwifturl = f"https://zwiftpower.com/cache3/results/{zid}_zwift.json"
        try:
            assert self.session is not None
        except Exception as e:
            raise e
        if f"results_{zid}" in self.cached.keys() and refresh == False:
            return self.cached[f"results_{zid}"]
        else:
            with self.session.get(viewurl) as res:
                view = res.json()
            with self.session.get(zwifturl) as res:
                zwift = res.json()
            self.cached[f"results_{zid}"] = {'view_data': view['data'], 'zwift_data': zwift['data']}
        return self.cached[f"results_{zid}"]


def get_json_data_from_url(z_id):

    example = fetch_json(login_data=login_data)
    example.login()
    somedata = example.fetch_result(z_id)
    df = pd.DataFrame(somedata['view_data'])
    return df
