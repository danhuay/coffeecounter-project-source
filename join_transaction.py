import pandas as pd
import numpy as np
from cleaning_skus import sku_header_detail_combination
'''
This script is used to merge all transactions 2014-01-01 to 2017-09-01 with sku information df.
Main function clean_transactions(df, skus)
'''


def join_transactions(df, skus):
    '''
    Merge all transactions with SKU information. Do some cleaning. Main function.
    :param df: all transactions
    :param skus: SKU information
    :return: processed joint df
    '''
    df = filter_date(df)
    df = rm_zero_trans(df)
    joint_df = merge_sku_info(df, skus)
    joint_df = compute_lbs(joint_df)
    joint_df = compute_unit_price(joint_df)

    # convert created_at to datetime
    joint_df['created_at'] = pd.to_datetime(joint_df.created_at)

    return joint_df


def filter_date(df):
    '''
    Include transactions from 2014-01-01 to 2017-09-01 transactions only.
    :param df: df
    :return: processed df
    '''
    start_date = '2015-01-01'
    end_date = '2017-09-01'  # exclusive

    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    out_df = df[(df.created_at >= start_date) & (df.created_at < end_date)]

    return out_df


def rm_zero_trans(df):
    '''
    Remove rows with 0 quantity (fake transactions)
    :param df: df
    :return: processed df
    '''
    mask = (df.quantity == 0)
    return df[~mask]


def merge_sku_info(df, skus):
    '''
    Left join transactions with sku info df.
    :param df: transactions
    :param skus: sku info df
    :return: joint df, also prints out some shape info.
    '''
    joint_df = pd.merge(df, skus, how='left', on='sku')
    incld_df = joint_df[~joint_df.unit_lbs.isnull()]
    excld_df = joint_df[joint_df.unit_lbs.isnull()]

    # print some numbers.
    print("Total number of transactions: ", df.shape[0])
    print("Transactions with documented SKUs: ", incld_df.shape[0])
    print("Transactions missing documented SKUs: ", excld_df.shape[0])
    print("{0:.2f} % of transactions included for further analysis.".format(incld_df.shape[0] / df.shape[0] * 100))

    #     # visualize the distribution of missing items.
    #     incld_df.groupby('created_at')['customer_id'].count().plot.line()
    #     excld_df.groupby('created_at')['customer_id'].count().plot.line()
    #     plt.show()

    return incld_df


def compute_lbs(df):
    '''
    Calculate total weight by multiply quantity with unit weight.
    :param df: df
    :return: calculated df.
    '''
    df['lbs'] = df['unit_lbs'].multiply(df['quantity'])
    return df

def compute_unit_price(df):
    '''
    Calculate unit price.
    :param df: df
    :return: calculated df.
    '''
    df['unit_price'] = np.divide(df.loc[:, ['price']], df.loc[:, ['unit_lbs']])
    return df

def clean_transactions(file):
    '''
    Read transaction csv as dataframe.
    Clean transaction files. Remove 0 quantity transactions. Fill NaN unit price with other info.
    :param file: 'csv/cw_transactions.csv'
    :return: processed df
    '''
    df = rm_zero_trans(pd.read_csv(file))
    df.loc[df.price.isnull(), 'price'] = np.divide(df.loc[df.price.isnull(), 'line_item_net_sales'],
                                                   df.loc[df.price.isnull(), 'quantity'])
    return df


def join_transaction_sku(file1, file2, file3, file4):
    '''
    Combining all the information, to make a large joint df.
    :param file1: 'csv/workshop_skus_alltrans.csv'
    :param file2: 'csv/SKU_header.csv'
    :param file3: 'csv/SKU_detail.csv'
    :param file4: 'csv/cw_transactions.csv'
    :return: joint df.
    '''
    from cleaning_skus import sku_header_detail_combination
    skus = sku_header_detail_combination(file1, file2, file3, fileoutput=False)
    trans = clean_transactions(file4)
    df = join_transactions(trans, skus)
    return df


##############################################################

if __name__ == '__main__':
    print("Running join_transaction as a main file.")

    df = join_transaction_sku('csv/workshop_skus_alltrans.csv',
                         'csv/SKU_header.csv',
                         'csv/SKU_detail.csv',
                         'csv/cw_transactions.csv')

    print(df.dtypes)
