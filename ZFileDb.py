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
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.cached = {'results': f"{self.db_path}/results", 'teams': f"{self.db_path}/teams",
                       'profiles': f"{self.db_path}/profiles", 'teamlist': f"{self.db_path}/teamlist",
                       'live': f"{self.db_path}/live", 'wtrl_ttt': f"{self.db_path}/wtrl_ttt",
                       'avatar': f"{self.db_path}/avatar", 'results_list': f"{self.db_path}/results_list",
                       'event_list': f"{self.db_path}/event_list"}
        self.folder_setup()

    def folder_setup(self):
        for f in self.cached.values():
            makedirs(f, exist_ok=True)

    def check_cache(self, table, zid):
        file_path = f"{self.cached[table]}/{zid}.json"
        if isfile(file_path):
            with open(file_path, 'r') as j:
                data = json.load(j)
            return data
        else:
            return None

    def mostrecent(self, table, zid=None):
        dir_files = listdir(self.cached[table])
        if zid:
            dir_files = [f for f in dir_files if zid]
        if dir_files:
            dir_files = sorted(dir_files, reverse=True)
            with open(f"{self.cached[table]}/{dir_files[0]}", 'r') as j:
                data = json.load(j)
            return data
        else:
            return None

    def upsert(self, table, data):
        zid = data['zid']
        file_path = f"{self.cached[table]}/{zid}.json"
        with open(file_path, 'w') as j:
            json.dump(data, j)
    def save_avatar(self, file_path, avatar_file):
        with open(f"{self.cached['avatar']}/{file_path}", 'wb') as local_file:
            local_file.write(avatar_file.content)
