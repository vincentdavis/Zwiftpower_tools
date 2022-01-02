import logging
import configparser
from pymongo import MongoClient

class ZMongodb(object):
    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            mongoauth = config['MONGODB']['auth']
        except Exception as e:
            logging.info('login: Need a proper config.ini file or supply auth info')
            #default local
        try:
            self.client = MongoClient(mongoauth, tlsCAFile="zwift-WTRL mongodb ca-certificate.cer")
        except Exception:
            self.client = MongoClient()
        # database
        self.db = self.client.database
        self.collection = self.db['zwiftandmore']
        self.cached = {'results': self.db['results'], 'teams': self.db['teams'],
                       'profiles': self.db['profiles'], 'teamlist': self.db['teamlist'],
                       'live': self.db['live']}

    def check_cache(self, table, zid):
        # is_in_cache = self.cached[table].get(QID.zid == zid)
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


# class zwifting(BaseModel):
#     name: str
#     color: str


# class ResultView(BaseModel):
#     DT_RowId: None
#     ftp: int
#     friend: bool
#     pt: None
#     label: int
#     zid: int
#     pos: int
#     position_in_cat: int
#     name: str
#     cp: bool
#     zwid: int
#     res_id: float
#     lag: int
#     uid: int
#     time: list
#     time_gun: float
#     gap: float
#     vtta: None
#     vttat: bool
#     male: bool
#     tid: int
#     topen: bool
#     tname: str
#     tc: str
#     tbc: str
#     tbd: str
#     zeff: bool
#     category: str
#     height: list
#     max_hr: list
#     hrmax: list
#     hrm: bool
#     weight: list
#     power_type: int
#     display_pos: int
#     src: int
#     age: str
#     zada: bool
#     note: str
#     div: int
#     divw: int
#     skill: int
#     skill_b: int
#     skill_gain: int
#     np: list
#     hrr: list
#     hreff: list
#     avg_power: list
#     avg_wkg: list
#     wkg_ftp: list
#     wftp: list
#     wkg_guess: bool
#     wkg1200: list
#     wkg300: list
#     wkg120: list
#     wkg60: list
#     wkg30: list
#     wkg15: list
#     wkg5: list
#     w1200: list
#     w300: list
#     w120: list
#     w60: list
#     w30: list
#     w15: list
#     w5: list
#     is_guess: bool
#     upg: bool
#     penalty: None
#     reg: bool
#     fl: None
#     pts: None
#     pts_pos: None
#     info: bool
#     info_notes: list
#     log: bool
#     lead: bool
#     sweep: bool
#     actid: None
#     anal: bool


