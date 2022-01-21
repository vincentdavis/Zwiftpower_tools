import pandas as pd

def splitlist(df, col, drop2=True):
    df[[f'{col}', f'{col}_2']] = df[col].tolist()
    if drop2:
        df.drop(f'{col}_2', axis=1, inplace=True)


def field_timing(df, field_gap=1, time_field='time'):
    df['gap'] = df[time_field].diff(-1)
    df['field_split'] = df[time_field].diff(-1) < -1 * field_gap
    df.loc[df['field_split'], 'group_time'] = df[time_field]
    df['group_time'].fillna(method='ffill', inplace=True)
    # results[['name', 'time', 'gap', 'gap_bool', 'Group_Time']]

def team_time(df, team, time='gun_time', top=4):
    """
    data = ViewData api dataframe
    team can be a list of rider zwid or a tname tag.
    """
    if isinstance(team, 'str'):
        team_result = {'team_times': df[df.tname == team].nsmallest(4, time) [['zwid', time]].to_dict(orient='records')}
        team_result['team_total_time'] = df[df.tname == team].nsmallest(4, 'time')[time].sum(axis=0)
    elif isinstance(team, 'list'):
        team_result = {'team_times': df[df.zwid.isin(team)].nsmallest(4, time)[['zwid', time]].to_dict(orient='records')}
        team_result['team_total_time'] = df[df.zwid.isin(team)].nsmallest(4, 'time')['time'].sum(axis=0)

def combine_on_zwid(df_base, df_add):
    """
    This is a simple merge, Add columns in df_add to matching rows by zwid to df_base
    If not match from df_add is found in df_base, it is ignored
    If a row in df_base does not match a row in df_add, NA is added
    """
    pass

def calculate_sprints(df, sprint_names=None):
    """
    - splits msec, watts, wkg columns
    - sprint_names dict(num:name)

    """
    for col in ['msec', 'watts', 'wkg']:
        temp = pd.json_normalize(df[col])
        if sprint_names:
            temp.rename(columns={k:f"{col}_{sprint_names[k]}" for k in temp.columns}, inplace=True)
        else:
            temp.rename(columns={k: f"{col}_{k}" for k in temp.columns}, inplace=True)
        df = pd.concat([df, temp], axis=1)

def rank_fts(df, sprints, group_col='category'):
  """
  You can choose different group_col and sort_col
  if grou_col is none, then do not group
  """
  for sp in sprints:
      if group_col is not None:
          ranks = df.groupby(group_col)[sp].rank(ascending = True, method = 'first')
          ranks.name = f"fts_{group_col}_{sp}_rank"
      else:
        ranks = df.rank(ascending = True, method = 'first')
  return pd.concat([df, ranks], axis=1)

def melt_to_rows(df):
    """
    Put each sprint result on a row
    """
    dont_melt_col = [col for col in df.columns if 'msec_' not in col]
    melt_col = [col for col in df.columns if 'msec_' in col]
    s_long = pd.melt(df, id_vars=dont_melt_col,
                     value_vars=melt_col,
                     var_name='Sprint', value_name='sprint_msec').sort_values('fts_category_13_msec_rank')
    return df





