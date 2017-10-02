import pandas as pd
from join_transaction import join_transaction_sku
from selling_channel_split import splitting_channels


def to_web_data(df, b2c=False):
    '''
    Creat a csv file appropiate for DC.js visuallization.
    : param df:, dataframe needs to be processed
    : b2c=False, b2c channel with extra source info about channels
    : return a ndf that to be saved in dc.js.
    : auto saves csv file in the directory.
    '''
    ndf = df.loc[:, ['created_at', 'source', 'origin', 'blend', 'roast_level', 'type', 'unit_price', 'lbs']]
    ndf = ndf.dropna()
    ndf['year'] = ndf.created_at.dt.year
    ndf['month'] = ndf.created_at.dt.month

    if b2c:
        ndf.source = ndf.source.map({'DTC': 'Online', 'Retail': 'In Store'})
        output_df = ndf.groupby(['year', 'month', 'origin', 'source',
                                 'blend', 'roast_level', 'type']).sum()['lbs'].reset_index()
        output_df['unit_price'] = ndf.groupby(['year', 'month', 'origin', 'source',
                                               'blend', 'roast_level', 'type']).mean()['unit_price'].values
        output_df.rename(columns={'lbs': 'sales'}, inplace=True)
    else:
        output_df = ndf.groupby(['year', 'month', 'origin', 'blend', 'roast_level', 'type']).sum()['lbs'].reset_index()
        output_df['unit_price'] = ndf.groupby(['year', 'month', 'origin', 'blend', 'roast_level', 'type']).mean()[
            'unit_price'].values
        output_df.rename(columns={'lbs': 'sales'}, inplace=True)

    return output_df

#####################################################
if __name__ == '__main__':

    all_trans = join_transaction_sku('csv/workshop_skus_alltrans.csv',
                         'csv/SKU_header.csv',
                         'csv/SKU_detail.csv',
                         'csv/cw_transactions.csv')

    for source in ['b2c', 'b2b', 'retail']:
        df = splitting_channels(all_trans, output = source)
        output = to_web_data(df, b2c = (source == 'b2c'))
        output.to_csv('csv/web/' + source + '.csv', index = False)
