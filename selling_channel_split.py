import pandas as pd
import numpy as np

from join_transaction import join_transaction_sku


def splitting_channels(df, output = ''):
    '''
    Split selling channels.
    :param df: df
    :param output: string, which channel to output 'b2c', 'b2b', or 'retail'
    B2C individual customers: Retail + DTC
    daily customers: Wholesale & Internal
    B2B: Wholesale others
    '''
    b2c = (df.source == 'DTC') | (df.source == 'Retail')
    b2b = (df.source == 'Wholesale') & (df.unit_type != 'Internal')
    retail = (df.source == 'Wholesale') & (df.unit_type == 'Internal')

    b2c = df[b2c]
    b2b = df[b2b]
    retail = df[retail]

    if output == 'b2c':
        print("Slicing " + output.upper() + ", containing %d rows." % b2c.shape[0])
        return b2c
    elif output == 'b2b':
        print("Slicing " + output.upper() + ", containing %d rows." % b2b.shape[0])
        return b2b
    elif output == 'retail':
        print("Slicing " + output.upper() + ", containing %d rows." % retail.shape[0])
        return retail
    else:
        raise ValueError('Please specify which selling channels to output: b2b, b2c, retail using `output =` ')


##############################################

if __name__ == '__main__':

    print('Running selling_channel_split as a main file.')
    df = join_transaction_sku('csv/workshop_skus_alltrans.csv',
                         'csv/SKU_header.csv',
                         'csv/SKU_detail.csv',
                         'csv/cw_transactions.csv')

    x = splitting_channels(df, output='b2c')
    print(x.columns)


