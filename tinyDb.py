from tinydb import TinyDB
from tinydb import Query


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
