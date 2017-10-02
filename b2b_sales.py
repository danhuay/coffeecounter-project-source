import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from join_transaction import join_transaction_sku
from selling_channel_split import splitting_channels
from plot_functions import plot_trend_and_relationships
from regression_pipeline import linear_regression, forecast_b2b
from scipy.stats import norm



def accum_customer_numbers(file):
    '''
    from the first time customer appears calculate the new customer every month.
    file: csv file that contain unique customer id and the first time they appeared in the system
    return dataframe contains monthly new customers
    '''
    from join_transaction import filter_date
    all_customers = pd.read_csv(file)
    all_customers = filter_date(all_customers)
    all_customers_unique = all_customers[~all_customers.customer_id.duplicated()]
    all_customers_unique = all_customers_unique.set_index(all_customers_unique.created_at).drop('created_at', axis=1)
    all_customers_unique = all_customers_unique.resample('M').count().cumsum()
    return all_customers_unique

def elapsed_month(df):
    '''
    Calculate elapsed month since starting date
    :param df: dataframe containing time info
    :return: modified dataframe
    '''
    length = df.shape[0]
    df['elapsed_month'] = np.linspace(1, length, length)
    return df

def monthly_sales_vs_customers(file):
    '''
    combining monthly sales with new customer numbers
    :param file: csv datafile contain unique customer id and the first time they appeared in the system
    :return: dataframe containing information
    '''
    customers = accum_customer_numbers(file)
    monthly_sales = pd.DataFrame(df.set_index(df.created_at)['lbs'].resample('M').sum())
    monthly_sales = monthly_sales.join(customers)
    monthly_sales = elapsed_month(monthly_sales)
    return monthly_sales


if __name__ == '__main__':
    # import all transaction data
    all_trans = join_transaction_sku('csv/workshop_skus_alltrans.csv',
                         'csv/SKU_header.csv',
                         'csv/SKU_detail.csv',
                         'csv/cw_transactions.csv')
    # slicing only b2b
    df = splitting_channels(all_trans, output = 'b2b')
    # monthly new customers added
    monthly_sales = monthly_sales_vs_customers('csv/cw_customers.csv')
    # plot trend
    plot_trend_and_relationships(monthly_sales.index, monthly_sales.customer_id, monthly_sales.lbs,
                                 time_locations='index',
                                 xylabels=('Number of Customers', 'Monthly Sales'),
                                 savefig='img/b2b.png')
    # linear regression, monthly sales vs. customer numebers.
    customer_sales_reg = linear_regression(monthly_sales.customer_id, monthly_sales.lbs)
    # linear regression, number of customers vs. datetime
    elapsed_month_customer_reg = linear_regression(monthly_sales.elapsed_month, monthly_sales.customer_id)
    # plot distributions of residuals
    residuals = monthly_sales.lbs - customer_sales_reg.predict(monthly_sales.customer_id.values.reshape(-1, 1))
    sns.distplot(residuals, bins=10, fit=norm)
    plt.show()
    # forecast 2018 b2b sales
    forecast = forecast_b2b(2018, elapsed_month_customer_reg, customer_sales_reg)

