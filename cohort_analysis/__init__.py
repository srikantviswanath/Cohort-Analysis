import pandas as pd
import datetime
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 10000)

orders = pd.read_csv('data_sources/orders.csv', ',')
customers = pd.read_csv('data_sources/customers.csv')
joined = pd.merge(orders, customers, how='inner', left_on='user_id', right_on='id')[['id_x', 'user_id', 'created_x', 'created_y']]
joined = joined.rename(
    index=str,
    columns={
        'id_x': 'OrderID',
        'user_id': 'UserID',
        'created_x': 'OrderCreatedTS',
        'created_y': 'SignUpTS'
    }
)
joined['SignUpTS'] = joined['SignUpTS'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
joined['OrderCreatedTS'] = joined['OrderCreatedTS'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
joined['Delta'] = (joined['OrderCreatedTS'] - joined['SignUpTS']).apply(lambda x: x.days)
min_delta, max_delta = joined['Delta'].min(), joined['Delta'].max()
delta_bins = list(range(joined['Delta'].min(), joined['Delta'].max() + 7, 7))
joined['DeltaBins'] = pd.cut(
    joined.Delta,
    delta_bins,
    labels=['{}-{} days'.format(b, e) for b, e in zip(delta_bins, delta_bins[1:])],
    include_lowest=True
)
earliest_date, latest_date = min(joined['SignUpTS']), max(joined['SignUpTS'])
sign_up_cohorts = pd.date_range(start=earliest_date, end=latest_date + datetime.timedelta(days=7), freq='7D')
sign_up_bins = [d.toordinal() for d in sign_up_cohorts.date]
sign_up_cohort_labels = ['{}/{}-{}/{}'.format(b.month, b.day, e.month, e.day) for b,e in zip(sign_up_cohorts, sign_up_cohorts[1:])]
joined['SignUpTSOrdinal'] = joined['SignUpTS'].apply(lambda x: x.toordinal())
joined['SignUpCohorts'] = pd.cut(joined.SignUpTSOrdinal, sign_up_bins, labels=sign_up_cohort_labels, include_lowest=True)
joined = joined.drop_duplicates(['SignUpCohorts', 'DeltaBins', 'UserID'])
#joined = joined.sort_values(by=['SignUpCohorts', 'DeltaBins'])[['OrderID', 'UserID', 'SignUpCohorts', 'DeltaBins', 'SignUpTS', 'OrderCreatedTS']]

#joined = pd.groupby(joined, ['SignUpCohorts', 'DeltaBins']).agg({'UserID': pd.Series.nunique}).reset_index()
joined = pd.crosstab(joined.SignUpCohorts, joined.DeltaBins, margins=True)

for col in joined.columns[:-1]:
    joined[col] = joined.apply(lambda row: '{:.2f} % orderers ({})'.format(row[col] / row['All'] * 100, row[col]), axis=1)

print(joined)
#print(pd.pivot_table(joined, index=['SignUpCohorts', 'DeltaBins'], values='UserID', aggfunc=pd.Series.nunique))
#def map_cohort_dates(start_date, cohort_size=7):
 #   pass
#print(pd.qcut(joined['SignUpTS'], 10))
