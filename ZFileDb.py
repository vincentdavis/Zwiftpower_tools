from os import makedirs, listdir
from os.path import isfile
import json


class ZFileDb(object):
    """
    database class needs to have:
    check_cache:
    mostrecent:
    upsert
    """
    def __init__(self, db_path='database/ZFileDb'):
        self.db_path = db_path
        self.cached = {'results': f"{self.db_path}/results", 'teams': f"{self.db_path}/teams",
                       'profiles': f"{self.db_path}/profiles", 'teamlist': f"{self.db_path}/teamlist",
                       'live': f"{self.db_path}/live", 'wtrl_ttt': f"{self.db_path}/wtri_ttt"}
    def folder_setup(self):
        for f in self.cached.values():
            makedirs(f, exist_ok=True)

    def check_cache(self, table, zid):
        file_path = f"{self.cached[table]}/{zid}"
        if isfile(file_path):
            with open(file_path, 'r') as j:
                data = json.load(j)
            return data
        else:
            return None

    def mostrecent(self, table):
        dir_files = listdir(self.cached[table])
        dir_files = [f for f in dir_files if ]
        def sort_timstamp(x):
            return (x.split("_")[0])
        dir_files = sorted(dir_files, key=sort_timstamp, reverse=True)
        return dir_files[0]
        else:
            return None

    def upsert(self, table, data):
        file_path = f"{self.cached[table]}/{zid}"
        with open(file_path, 'w') as j:
            data = json.dump(data, j)
