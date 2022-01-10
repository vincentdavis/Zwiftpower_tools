import pytest
from os.path import isdir
from os import remove, makedirs
from fetch import FetchJson
from ZFileDb import ZFileDb


# def test_setup_database():
#     db = ZFileDb(db_path="temp_data/database/ZFileDb")
#     for folder in db.cached.values():
#         assert isdir(folder)
#
#
# def test_login():
#     # Define the database
#     db = ZFileDb(db_path="temp_data/database/ZFileDb")
#     f = FetchJson(db=db)
#     f.login()
#     assert "Zwift Profile" in f.session.get("https://zwiftpower.com").text


@pytest.fixture(scope='session')
def z():
    print("##-setting up fixture-##")
    db = ZFileDb(db_path="temp_data/database/ZFileDb")
    f = FetchJson(db=db)
    f.login()
    return f

@pytest.fixture(scope="session")
def dirs():
    makedirs("temp_data", exist_ok=True)

def test_fetch_result(z, dirs):
    try:
        result, cache = z.fetch_result(2600544, refresh=False)
        assert cache == "refresh"
        result, cache = z.fetch_result(2600544, refresh=False)
        assert cache == "cache"
        view_data_keys = ['DT_RowId', 'ftp', 'friend', 'pt', 'label', 'zid', 'pos', 'position_in_cat', 'name', 'cp', 'zwid', 'res_id', 'lag', 'uid', 'time', 'time_gun', 'gap', 'vtta', 'vttat', 'male', 'tid', 'topen', 'tname', 'tc', 'tbc', 'tbd', 'zeff', 'category', 'height', 'flag', 'avg_hr', 'max_hr', 'hrmax', 'hrm', 'weight', 'power_type', 'display_pos', 'src', 'age', 'zada', 'note', 'div', 'divw', 'skill', 'skill_b', 'skill_gain', 'np', 'hrr', 'hreff', 'avg_power', 'avg_wkg', 'wkg_ftp', 'wftp', 'wkg_guess', 'wkg1200', 'wkg300', 'wkg120', 'wkg60', 'wkg30', 'wkg15', 'wkg5', 'w1200', 'w300', 'w120', 'w60', 'w30', 'w15', 'w5', 'is_guess', 'upg', 'penalty', 'reg', 'fl', 'pts', 'pts_pos', 'info', 'info_notes', 'log', 'lead', 'sweep', 'actid', 'anal']
        zwift_data_keys = ['DT_RowId', 'name', 'watts', 'wkg', 'bpm', 'hrm', 'race_time', 'time_diff', 'zwid', 'label', 'dq_cat', 'pos', 'power_type', 'wkg_ftp', 'wkg1200', 'lagp', 'events']
        assert list(result['view_data'][0].keys()) == view_data_keys
        assert list(result['zwift_data'][0].keys()) == zwift_data_keys
    except Exception as e:
        raise e
    finally:
        remove("temp_data/database/ZFileDb/results/2600544.json")

def test_result_list(z, dirs):
    z.result_list(refresh=False)
    result, cache = z.result_list(refresh=False)
    assert cache == "cache"
    result_list_fields = ['DT_RowId', 'friends', 'tent', 'f_list', 'tent_list', 'km', 'tm', 'r', 't', 'zid', 'rid', 'spi', 'spl', 'f', 'zcl',
     'rt', 'layout', 'layout_w', 'rk', 'laps', 'cats', 'signups', 'stag', 'w', 'dur', 'dir', 'f_t', 'f_km', 'f_time',
     'f_day', 'f_w', 'f_ru', 'f_r', 'rtype', 'eid', 'rules', 'crules', 'cul', 'fin', 'ctype', 'tags', 'recur', 'lbl']
    assert list(result['results_list'][0].keys()) == result_list_fields

def test_event_list(z, dirs):
    z.event_list(refresh=False)
    result, cache = z.event_list(refresh=False)
    print(list(result['event_list'][0].keys()))
    assert cache == "cache"
    # result_list_fields = ['DT_RowId', 'friends', 'tent', 'f_list', 'tent_list', 'km', 'tm', 'r', 't', 'zid', 'rid', 'spi', 'spl', 'f', 'zcl',
    #  'rt', 'layout', 'layout_w', 'rk', 'laps', 'cats', 'signups', 'stag', 'w', 'dur', 'dir', 'f_t', 'f_km', 'f_time',
    #  'f_day', 'f_w', 'f_ru', 'f_r', 'rtype', 'eid', 'rules', 'crules', 'cul', 'fin', 'ctype', 'tags', 'recur', 'lbl']
    # assert list(result['results_list'][0].keys()) == result_list_fields

