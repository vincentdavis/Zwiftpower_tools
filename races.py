def splitlist(df, col, drop2=True):
    df[[f'{col}', f'{col}_2']] = df[col].tolist()
    if drop2:
        df.drop(f'{col}_2', axis=1, inplace=True)


def field_timing(results, field_gap=1, time_field='time'):
    results
    results['gap'] = results[time_field].diff(-1)
    results['field_split'] = results[time_field].diff(-1) < -1 * field_gap
    results.loc[results['field_split'], 'group_time'] = results[time_field]
    results['group_time'].fillna(method='ffill', inplace=True)
    # results[['name', 'time', 'gap', 'gap_bool', 'Group_Time']]

def dg_filter():
    pass
