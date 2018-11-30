import unittest
import pandas as pd
from cohort_analysis import transform
import datetime as dt


class TestTransformDataFrame(unittest.TestCase):

    def setUp(self):
        self.df_tz_conversion = pd.DataFrame.from_dict({
            'Col1': ['2015-07-03 22:01:11', '2015-11-13 07:01:11', '2017-8-13 12:01:11'],
        })
        self.df_cohort_period = pd.DataFrame.from_dict({
            'CohortDate': [dt.datetime(2018, 1, 1, 12, 50), dt.datetime(2018, 5, 1, 16, 50)],
            'Anchor': [dt.datetime(2018, 1, 3, 13, 50), dt.datetime(2018, 5, 1, 17, 50)]
        })

    def test_df_str_to_datetime_UTC(self):
        """convert str datetime to datetime date in the default UTC tz"""
        transformed_df = transform.df_str_to_datetime(self.df_tz_conversion, ['Col1'])
        self.assertEqual(transformed_df.iloc[0].tzname(), 'UTC')

    def test_df_str_to_datetime_US_Eastern(self):
        """convert to US/Eastern tz"""
        transformed_df = transform.df_str_to_datetime(self.df_tz_conversion, ['Col1'], tz='US/Eastern')
        self.assertEqual(transformed_df.iloc[0].tzname(), 'EDT')

    def test_calculate_cohort_period_days(self):
        transformed_df = transform.calculate_cohort_period(self.df_cohort_period, 'Anchor')
        self.assertEqual(transformed_df['CohortPeriod'].values.tolist(), [2, 0])

    def test_calculate_cohort_period_hours(self):
        transformed_df = transform.calculate_cohort_period(self.df_cohort_period, 'Anchor', extract='seconds')
        self.assertEqual(transformed_df['CohortPeriod'].values.tolist(), [3600, 3600])


class TestDataframeBinning(unittest.TestCase):

    def test_generate_bins_dates(self):
        """Generating bins of column of dates"""
        df = pd.DataFrame.from_dict({
            'Column': [dt.date(2018, 1, 1), dt.date(2018, 1, 13), dt.date(2018, 1, 18), dt.date(2018, 1, 2), dt.date(2018, 2, 1)],
        })
        bin_nums, bin_labels = transform.generate_bins(df, 'Column', 7)
        self.assertEqual(bin_nums, [736695, 736702, 736709, 736716, 736723, 736730])
        self.assertEqual(bin_labels, ['1/1-1/8', '1/8-1/15', '1/15-1/22', '1/22-1/29', '1/29-2/5'])

    def test_generate_bins_ints(self):
        """Generating bins of column of ints"""
        df = pd.DataFrame.from_dict({
            'Column': [3, 5, 6, 8, 9],
        })
        bin_nums, bin_labels = transform.generate_bins(df, 'Column', 2, label_suffix='potatoes')
        self.assertEqual(bin_nums, [3, 5, 7, 9])
        self.assertEqual(bin_labels, ['3-5potatoes', '5-7potatoes' , '7-9potatoes'])

    def test_generate_bins_str_raises(self):
        """Generating bins of column of str. Raises"""
        df = pd.DataFrame.from_dict({
            'Column': ['3', '5', '6', '8', '9'],
        })
        with self.assertRaises(ValueError):
            transform.generate_bins(df, 'Column', 2)


if __name__ == '__main__':
    unittest.main()
