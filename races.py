
def splitlist(df, col, drop2=True):
    df[[f'{col}', f'{col}_2']] = df[col].tolist()
    if drop2:
        df.drop(f'{col}_2', axis=1, inplace=True)

def field_timing(results, field_gap=2):
    results['gap'] =