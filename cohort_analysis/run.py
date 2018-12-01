from cohort_analysis.extract import extract_csv_files
import pandas as pd
from cohort_analysis import constants as cts
from cohort_analysis import transform

COHORT_ANALYSIS_CONFIG = {
    'cohort_period_size': 7,
    'cohort_date_size': 7,
}

def cohort_analysis(data_file_paths, keys):
    dfs = extract_csv_files(data_file_paths)
    df = transform.join_and_rename(*dfs, *keys, rename_map={
        'id_x': cts.ORDER_ID,
        'user_id': cts.USER_ID,
        'created_x': cts.ORDER_TS,
        'created_y': cts.COHORT_DATE
    })
    df = transform.df_str_to_datetime(df, [cts.COHORT_DATE, cts.ORDER_TS], tz='UTC')
    df = transform.calculate_cohort_period(df, cts.ORDER_TS)
    cohort_period_bins, cohort_period_labels = transform.generate_bins(df, cts.COHORT_PERIOD, 7, label_suffix='days')
    df = transform.binnify(df, cts.COHORT_PERIOD, cohort_period_labels, cohort_period_bins, cts.COHORT_PERIOD)
    cohort_date_bins, cohort_date_labels = transform.generate_bins(df, cts.COHORT_DATE, 7)
    df[cts.COHORT_DATE] = df[cts.COHORT_DATE].apply(lambda date: date.toordinal())
    df = transform.binnify(df, cts.COHORT_DATE, cohort_date_labels, cohort_date_bins, cts.COHORT_DATE)
    df = df.drop_duplicates([cts.COHORT_DATE, cts.COHORT_PERIOD, cts.USER_ID])
    df = pd.crosstab(getattr(df, cts.COHORT_DATE), getattr(df, cts.COHORT_PERIOD), margins=True)
    df = transform.calculate_pct(df, 'All')
    df = df.rename(index=str, columns={'All': 'Customers'})
    columns = df.columns.tolist()
    return df[columns[-1:] + columns[:-1]]


def run(data_file_paths):
    return cohort_analysis(data_file_paths, ('user_id', 'id'))


if __name__ == '__main__':
    print(run(['data_sources/orders.csv', 'data_sources/customers.csv']))