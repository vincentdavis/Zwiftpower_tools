from tinydb import TinyDB, Query
db = TinyDB('z_database.json')

table = db.table('teams')
table.insert({'value': True})