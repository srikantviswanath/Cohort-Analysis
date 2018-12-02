from cohort_analysis.extract import extract_csv_files
import pandas as pd
from cohort_analysis import constants as cts
from cohort_analysis import transform

COHORT_ANALYSIS_CONFIG = {
    'cohort_period_window': 7,  # e.g., 7-14 days cohort period
    'cohort_date_window': 7,  # e.g., 1/1 - 1/8
    'cohort_periods_width': 8,  # total number of cohort periods to display
}

def cohort_analysis(data_file_paths, keys, cohort_config, rename_map={}):
    dfs = extract_csv_files(data_file_paths)
    df = transform.join_and_rename(*dfs, *keys, rename_map=rename_map)
    df = transform.df_str_to_date(df, [cts.COHORT_DATE, cts.ORDER_TS], tz='UTC')
    df = transform.calculate_cohort_period(df, cts.ORDER_TS)
    cohort_period_bins, cohort_period_labels = transform.generate_bins(
        df, cts.COHORT_PERIOD, cohort_config['cohort_period_window'], label_suffix='days'
    )
    df = transform.binnify(df, cts.COHORT_PERIOD, cohort_period_labels, cohort_period_bins, cts.COHORT_PERIOD)
    cohort_date_bins, cohort_date_labels = transform.generate_bins(df, cts.COHORT_DATE, cohort_config['cohort_date_window'])
    df[cts.COHORT_DATE] = df[cts.COHORT_DATE].apply(lambda date: date.toordinal())
    df = transform.binnify(df, cts.COHORT_DATE, cohort_date_labels, cohort_date_bins, cts.COHORT_DATE)
    df = df.drop_duplicates([cts.COHORT_DATE, cts.COHORT_PERIOD, cts.USER_ID])
    df = pd.crosstab(getattr(df, cts.COHORT_DATE), getattr(df, cts.COHORT_PERIOD), margins=True)
    columns = df.columns.tolist()
    df = df[columns[-1:] + columns[:cohort_config['cohort_periods_width']]]
    df = transform.calculate_pct(df, 'All', suffix='orderers')
    return df.rename(index=str, columns={'All': 'Customers'})


def run(data_file_paths, keys, cohort_config, rename_map={}):
    analysed_df =  cohort_analysis(data_file_paths, keys, cohort_config, rename_map)
    analysed_df.to_csv('analysed_data/orders_signup_dates.csv')
    return analysed_df


if __name__ == '__main__':
    print(run(
        ['data_sources/orders.csv', 'data_sources/customers.csv'], ('user_id', 'id'), COHORT_ANALYSIS_CONFIG,
        rename_map={
        'id_x': cts.ORDER_ID,
        'user_id': cts.USER_ID,
        'created_x': cts.ORDER_TS,
        'created_y': cts.COHORT_DATE
    }))