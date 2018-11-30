from cohort_analysis.extract import extract_csv_files
import pandas as pd
from cohort_analysis import constants
from cohort_analysis import transform

COHORT_ANALYSIS_CONFIG = {

}

def cohort_analysis(data_file_paths, keys):
    dfs = extract_csv_files(data_file_paths)
    df = transform.join_and_rename(*dfs, *keys, rename_map={
        'id_x': constants.ORDER_ID,
        'user_id': constants.USER_ID,
        'created_x': constants.ORDER_CREATED_TS,
        'created_y': constants.COHORT_DATE
    })
    df[constants.COHORT_DATE] = pass


def run(data_file_paths):
    cohort_analysis(data_file_paths, ('user_id', 'id'))


if __name__ == '__main__':
    run(['data_sources/orders.csv', 'data_sources/customers.csv'])