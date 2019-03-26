def valid_open_runners(df):
    df = df.loc[df.started]  # Keep only started
    df = df.reset_index(drop=True, inplace=False)  # Make sure runners (i.e. rows) have unique index
    for (key, runner) in df.iterrows():
        include = False
        if runner.classname.lower().startswith('ö'):
            if runner.birthyear is not None:
                if (runner.age <= 16) & (runner.age >= 5):
                    include = True
        else:  #"inskolning" or U-class
            if runner.birthyear is not None:
                if (runner.age <= 16) & (runner.age >= 5):
                    include = True

        df.at[key, 'include'] = include

    df = df.loc[df.include]
    df = df.drop(columns=['include'])
    return df