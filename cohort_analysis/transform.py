import pandas as pd
import datetime
import pytz
import numpy as np
from .constants import COHORT_PERIOD, COHORT_DATE


def join_and_rename(
    df_left, df_right,
    df_left_key='id',
    df_right_key='id',
    join_type='inner',
    project='all',
    rename_map={}
):
    """
    Join and rename(optional) 2 pandas dataframes
    :param pd.Dataframe df_left:
    :param pd.Dataframe df_right:
    :param str join_type: one of inner, outer, left, right
    :param str df_left_key: left df join key
    :param str df_right_key: right df join key
    :param list project: columns to project/retain. 'all' will be defaulted to retain all columns
    :param dict rename_map: Optional mapping to rename a subset of columns
    :return:
    """
    joined = pd.merge(df_left, df_right, how=join_type, left_on=df_left_key, right_on=df_right_key)
    joined = joined[project] if project != 'all' else joined
    return joined.rename(index=str, columns=rename_map)


def df_str_to_date(df, cols, datetime_format='%Y-%m-%d %H:%M:%S', tz='UTC'):
    """
    Given a str representation of datetime, convert into a datetime.date for a given timezone
    :param pd.DataFrame df:
    :param list cols: datetime str cols to transform
    :param str datetime_format:
    :param str tz: default to UTC. If not UTC then, first convert to UTC datetime object and then convert to local tz
    :return pd.DataFrame:
    """
    for col in cols:
        df[col] = df[col].apply(lambda x: datetime.datetime.strptime(x, datetime_format).replace(tzinfo=pytz.timezone('UTC')))
        if tz != 'UTC':
            df[col] = df[col].apply(lambda x: x.astimezone(pytz.timezone(tz)))
        df[col] = df[col].apply(lambda x: x.date())
    return df


def calculate_cohort_period(df, period_end_col, extract='days'):
    """
    Given a DataFrame with column 'CohortDate', calculate the delta time until :period_end_col:
    :param pd.DataFrame df:
    :param str period_end_col: Column used to calculate the cohort period from 'CohortDate'
    :param str extract: Specific attribute of datetime.timedelta. Defaulted to days
    :return pd.DataFrame: DataFrame with CohortPeriod column populated
    """
    df[COHORT_PERIOD] = (df[period_end_col] - df[COHORT_DATE]).apply(lambda x: getattr(x, extract))
    return df


def generate_bins(df, col, bin_size, label_suffix=''):
    """
    For a given DataFrame and a column, generate a range of bin labels starting from minimum to maximum of the :col:
    with each bin label of size :bin_size:
    :param pd.DataFrame df:
    :param str col:
    :param int bin_size:
    :return (list, list): numerical representation of bins used for pd.cut, str representation of the bins for display
    """
    min_val, max_val = df[col].min(), df[col].max()
    if isinstance(min_val, (datetime.date)):
        bins = pd.date_range(start=min_val, end=max_val + datetime.timedelta(days=bin_size), freq=str(bin_size) + 'D')
        return [d.toordinal() for d in bins.date], \
               ['{}/{}-{}/{}{}'.format(b.month, b.day, e.month, e.day, label_suffix) for b,e in zip(bins, bins[1:])]
    elif isinstance(min_val, np.integer):
        bins = list(range(min_val, max_val + bin_size, bin_size))
        return bins, ['{}-{}{}'.format(b, e, label_suffix) for b, e in zip(bins, bins[1:])]
    else:
        raise ValueError('Need int or date types for generating bins')


def binnify(df, input_col, bin_labels, bin_values, binned_col_name):
    """
    Assign bins to values in the :input_col: using :bin_labels: and :bin_values:
    :param pd.DataFrame df:
    :param str input_col: The column used as input for binning
    :param [str] bin_labels: List of bin labels/Categorical values to be applied
    :param [int] bin_values: List of int bin values used in the actual binning process
    :param str binned_col_name: Column name to be used to store bin results
    :return pd.DataFrame: DataFRame with a new column :binned_col_name: containing binned output
    """
    df[binned_col_name] = pd.cut(getattr(df, input_col), bin_values, labels=bin_labels, include_lowest=True)
    return df


def calculate_pct(df, total_col, pct_precision=2, suffix=''):
    """
    Given a DataFrame with hits/purchases for various cohort period columns and a total(:total_col:) column,
    calculate corresponding percentages for purchases in each cohort group
    :param pd.DataFram df:
    :param str total_col:
    :return pd.DataFrame: cohort period columns' hits/purchases transformed into percentages w.r.t total_column
    """
    total_col_index = df.columns.get_loc(total_col)
    for col in df.columns[:total_col_index].tolist() + df.columns[total_col_index+1:].tolist():
        df[col] = df.apply(
            lambda row: '{} % {}({})'.format(round(row[col] / row[total_col] * 100, pct_precision), suffix, row[col]),
            axis=1
        )
    return df