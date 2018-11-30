import pandas as pd


def extract_csv_files(input_files, separator=','):
    """
    Given a tuple of csv files with their full paths, extract and return a list of pd.Dataframes
    :param tuple input_files:
    :return [pd.Dataframes]:
    """
    return [pd.read_csv(f, sep=separator) for f in input_files]


