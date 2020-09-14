from datetime import date
from tinydb import TinyDB, Query
from tinydb.operations import set
from zp_tools import *

"""
Utilities for updating local nosql database
You need to configure these file locations
"""

db = TinyDB('z_database.json')
db_hist = TinyDB('z_database_hist.json')
Teams = db.table('Teams')
Teams_hist = db_hist.table('Teams')

db_teams_racer = TinyDB('z_database_teams_racers.json')
Teams_Racers = db_teams_racer.table('Teams_Racers')

db_racers = TinyDB('z_database_racers.json')
Racers = db_racers.table('Racers')



def update_team_list(teams=Teams, teams_hist=Teams_hist):
    """
    we get the list of all teams and save the basic team stats
    """
    zp_team_list = get_team_list()
    qteams = Query()
    row_count = 0
    for ateam in zp_team_list.to_dict(orient='records'):
        row_count += 1
        instance_count = teams.count(qteams.team_id == ateam['team_id'])
        if instance_count > 0:
            old = teams.search(qteams.team_id == ateam['team_id'])[0]
            old_hist = teams_hist.insert(old)
            teams_hist.update(set('replaced_date', str(date.today())), doc_ids=[old_hist])
            teams.upsert(ateam, qteams.team_id == ateam['team_id'])
        else:
            Teams.upsert(ateam, qteams.team_id == ateam['team_id'])
        if not(row_count % 250):
            print(row_count)

def update_team_racers(team_id, Racers=Racers, Teams_Racers=Teams_Racers, session=None):
    """
    For a spesific team we:
    * get the list of racers
    * save that to a team <> racer table and with update stamp
    * Update the team racerer details
    Racers: racer databasae
    Teams_Racers: team <> racer database
    """
    if session==None:
        s = requests.Session()
    qracers = Query()
    trracers = Query()
    team_data = get_team_data(team_id, s=s)
    print(f"Number of racers: {len(team_data)}")
    assert(len(team_data)>0)
    for td in team_data.to_dict(orient='records'):
        td['record_date'] = str(date.today())
        r = Racers.upsert(td , qracers.zwid == td['zwid'])
        tr = {'record_date': str(date.today()), "zwid": td['zwid'], "team_id": team_id}
        Teams_Racers.upsert(tr, (trracers.team_id == team_id) & (trracers.zwid == td['zwid']))