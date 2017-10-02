import pandas as pd
'''
This file is aiming at combining SKUs with/without detailed information.
Unknown SKUs are identified via SKU encodings + keywords in the item_name column.
Blend/Single, Evergreen/Seasonal data are also decoded if possible.
The overall function will be `df = sku_header_detail_combination('workshop_skus_alltrans.csv', 'SKU_header.csv', 'SKU_detail.csv')`
'''


def sku_class(sku_header, sku_detail):
    '''
    The function uses a set of function to clean the SKU information obtained from client.
    :param sku_header: with SKU, item_name
    :param sku_detail: details about roasted level, seasonal etc.
    :return: a processed dataframe
    '''

    # merge the sku_header and sku_detail, leaving interesting features
    features = ['Category', 'Class', 'Subclass', 'Subclass Name',
                'Origin (if not described)', 'Roast Level ',
                'Type', 'Blend vs. Single', 'Green Cost/lb']
    df = pd.merge(sku_header, sku_detail, how='left', on='Subclass')
    df = df.loc[:, features]

    # creating sku_index, rename columns
    df = create_sku_index(df)

    # take care missing values, categorical features
    df = blend_or_single(df)
    df = microlot_geisha(df)
    df = is_seasonal(df)
    df = greenbean_costs(df)

    # rename columns
    df = renaming_columns(df)

    # roast level to lower case and then encode as categorical features
    df.roast_level = df.roast_level.str.lower()
    return df


def blend_or_single(df):
    '''
    Identified whether or not a coffee product is blend or single.
    Based on whether or not the origin column has ',' in it.
    :param df: merged dataframe of sku_header and sku_detail.
    :return: processed dataframe with labeled information.
    '''
    mask = df['Origin (if not described)'].str.contains(',')
    df.loc[mask, 'Blend vs. Single'] = 'Blend'
    df.loc[~mask, 'Blend vs. Single'] = 'Single'
    return df


def microlot_geisha(df):
    '''
    Map whether or not a coffee product is microlot or geisha beans.
    :param df: merged dataframe of sku_header and sku_detail.
    :return: Boolean mapped values of microlot or geisha.
    '''
    df['geisha'] = df.Type.map({'Geisha': True})
    df['microlot'] = df.Type.map({'Microlot': True})
    df.loc[:, ['geisha', 'microlot']] = df.loc[:, ['geisha', 'microlot']].fillna(value=False)
    return df


def is_seasonal(df):
    '''
    Map seasonal/evergreen features. Blends are always evergreen beans.
    :param df: merged dataframe of sku_header and sku_detail.
    :return: processed dataframe with labeled information.
    '''
    mask = (df.Type == 'Evergreen') | (df['Blend vs. Single'] == 'Blend')
    df.loc[mask, 'Type'] = 'Evergreen'
    df.loc[~mask, 'Type'] = 'Seasonal'
    return df


def greenbean_costs(df):
    '''
    Fill NA values of bean cost, based on mean values of certain origin/seasonal cahracters.
    Some origin without recorded cost price is labeled, use data from outside source.
    :param df: merged dataframe of sku_header and sku_detail.
    :return: data with proper cost filled in.
    '''
    df['Green Cost/lb'] = df['Green Cost/lb'].str.replace('$', '').astype(float)
    for types in ['Single', 'Blend']:
        origins = df.loc[df['Blend vs. Single'] == types, 'Origin (if not described)'].unique()
        for place in origins:
            mask = (df['Origin (if not described)'] == place)
            df.loc[mask, 'Green Cost/lb'] = df.loc[mask, 'Green Cost/lb'].fillna(df.loc[mask, 'Green Cost/lb'].mean())

    # catch exceptions: price from literatures
    price = {'Yemen': 6.81,
             'Zambia': 2.58,
             'Guatemala, Brazil ': 2.545}

    df.loc[df['Green Cost/lb'].isnull(), 'Green Cost/lb'] = df['Origin (if not described)'].map(price)
    return df


def create_sku_index(df):
    '''
    Creating sku index (typical first 5 letters)
    :param df: merged dataframe.
    :return: dataframe with new column sku_index
    '''
    df['sku_index'] = df.Category.str.strip() + df.Class.str.strip() + df.Subclass.str.strip()
    df['sku_index_length'] = df['sku_index'].str.len()
    df = df.drop_duplicates('sku_index')
    return df


def renaming_columns(df):
    '''
    Renaming the dataframe for conscise and easy referring.
    :param df: merged dataframe.
    :return: renamed dataframe.
    '''
    df.rename(columns={
        'Subclass Name': 'sub_name',
        'Origin (if not described)': 'origin',
        'Roast Level ': 'roast_level',
        'Green Cost/lb': 'cost',
        'Blend vs. Single': 'blend'}, inplace=True)

    old = df.columns.values
    new = [name.lower() for name in df.columns.values]
    renames = dict(zip(old, new))
    df.rename(columns=renames, inplace=True)
    return df

def all_skus(skus, df):
    '''
    Split all unique SKUs occured during the timespan depending on whether or not the SKU has proper info.
    :param skus: unique SKUs occured during the timespan
    :param df: proper encoded SKU detail dataframe (merged dataframe)
    :return: incld_df: data with proper info. excld_df: SKU without proper info.
    '''
    skus = sku_indexing(skus, df)
    jdf = pd.merge(skus, df, how='left', on='sku_index')
    jdf.sku_index_length.fillna(5, inplace=True)
    jdf.loc[:, 'sku_index_length'] = jdf.sku_index_length.astype(int)

    incld_df = jdf[~jdf.origin.isnull()]
    excld_df = jdf[jdf.origin.isnull()]
    return incld_df, excld_df


def sku_indexing(skus, df):
    '''
    From transaction SKUs extract their SKU headers. Also takes care of special cases (!=5)
    :param skus: dataframe of unique transactions
    :param df: dataframe of documented SKUs
    :return:
    '''
    skus['sku_index'] = skus.sku.str[0:5]
    special_sku = df[df.sku_index_length > 5].sku_index.values

    for sku in special_sku:
        skus.loc[skus.sku.str[0:len(sku)] == sku, 'sku_index'] = sku
    return skus


def extract_origin(df):
    '''
    Extracting origin / blends from item descriptions.
    :param df: dataframe with item names
    :return: dataframe with appended origin, blend values
    '''
    unknown = df[df.origin.isnull()]
    un_skus = unknown.drop_duplicates(subset='sku_index')
    un_skus = un_skus.dropna(axis=0, subset=['item_name'])
    un_skus['first_word'] = un_skus.item_name.str.split(' ').str[0]
    un_skus.origin = un_skus.apply(row_match, axis=1)
    un_skus.blend = un_skus.apply(match_blend, axis=1)
    return un_skus.drop(['first_word', 'sku'], axis=1)


def row_match(row):
    '''
    Pandas apply function. Taking care of those unnormal first words, map them into the correct ones.
    :param row: a Pandas dataframe row.
    :return: value of mapping.
    '''
    origins = ['Brazil', 'Colombia', 'Ethiopia', 'Nepal', 'Tanzania', 'Guatemala', 'Mexico',
               'Nicaragua', 'Rwanda', 'Ecuador', 'Congo', 'Burundi', 'Uganda', 'Panama', 'Kenya', 'Thailand',
               'Madagascar', 'Haiti']
    strange_origins = {'Costa': 'Costa Rica',
                       'Mexican': 'Mexico',
                       'Ethiopian': 'Ethiopia',
                       'Nyampinga': 'Rwanda'}

    if row.first_word in origins:
        return row.first_word
    elif row.first_word in strange_origins:
        return strange_origins[row.first_word]
    else:
        return 'Unknown'


def match_blend(row):
    '''
    Pandas apply function. Replace all the 'unknown' value to 'blend'
    :param row: pandas dataframe row
    :return: mapping value for the row
    '''
    if row.origin == 'Unknown':
        return 'Blend'
    else:
        return 'Single'


def excld_info(df):
    '''
    For those 50% without documented SKU information. Rejoin with the previous ones.
    :param df: dataframe with complete information
    :return: joint dataframe with all SKUs information
    '''
    sku = df.loc[:, ['sku', 'sku_index']]
    sku_info = extract_origin(df)
    jdf = pd.merge(sku, sku_info, how='left', on='sku_index')
    return jdf


def four_packs(df):
    ''''
    Take care of four pack products. multiply by 4 of their lbs.
    :param df: dataframe with complete information
    :return: corrected 4-pack info.
    '''
    four_pack = df[(df.sku_index.str[-1] == '4') & (df.sku_index_length > 5)].index.values
    for sku in four_pack:
        df.loc[sku, 'unit'] *= 4
    # print('Take care of 4 pack goods.')
    return df


def lb_or_oz(row):
    '''
    Pandas apply function. Take care or oz/lbs difference in 25 SKU.
    :param row: pandas dataframe row.
    :return: corrected values.
    '''
    try:
        if 'lb' in row:
            return 2.5
        else:
            return 2.5 / 16
    except:
        return 2.5 / 16


def unit_to_num(row):
    '''
    Pandas apply function. Mapping the SKUs weight infomation to actual lbs.
    :param row: pandas dataframe row.
    :return: values of lbs of the certain products.
    '''
    str_unit_mapping = {
        '01': 2.5 / 16,
        '05': 5,
        '08': 8 / 16,
        '10': 10 / 16,
        '12': 12 / 16,
        '50': 5 / 16,
        '70': 7 / 16,
        'HB': 12 / 16,
        'WB': 12 / 16
    }

    if row.str_unit == '25':
        return lb_or_oz(row.item_name)
    else:
        return str_unit_mapping[row.str_unit]


def create_unit(jdf):
    '''
    Create weight information for each product
    :param jdf: total dataframe
    :return:df with appended lbs info.
    '''
    df = jdf.loc[:, ['item_name', 'sku', 'sku_index', 'sku_index_length']]

    df['sku'] = df['sku'].str.replace('.', '')
    df['str_unit'] = df.sku.str[-4: -2]

    df['unit'] = df.apply(unit_to_num, axis=1)
    df = four_packs(df)
    jdf['unit_lbs'] = df['unit']

    return jdf

def sku_header_detail_combination(file1, file2, file3, fileoutput = False):
    '''
    Utlize all the functions to clean and join transaction skus and documented skus.
    :param file1: workshop_skus_alltrans.csv, all transaction skus from database.
    :param file2: sku_header.csv, documented skus (from excel)
    :param file3: sku_detail.csv, another part or infomation (fron excel)
    :param fileoutput: boolean, default False
    :return: output_df, a processed dataframe with all the infomation.
    '''
    skus = pd.read_csv(file1, usecols=(0, 1))
    skus.item_name = skus.item_name.fillna('Unknown')
    sku_header = pd.read_csv(file2)
    sku_detail = pd.read_csv(file3)

    # print('The shape of UNIQUE SKUs are:', skus.shape)
    # print('Shape of documented SKUs Header:', sku_header.shape)

    documented_sku = sku_class(sku_header, sku_detail)

    # print(documented_sku.shape)
    incld_df, excld_df = all_skus(skus, documented_sku)
    excld_df = excld_info(excld_df)
    joint_df = pd.concat([incld_df, excld_df])

    # make a copy of the joint_df, and make some adjustments.
    output_df = pd.DataFrame(create_unit(joint_df))

    # drop off irrelevant columns
    output_df.drop(['item_name', 'sku_index', 'category',
                    'class', 'subclass', 'sku_index_length'], axis=1, inplace=True)

    # output to csv files
    if fileoutput:
        output_df.to_csv('encoded_SKUs.csv', index=False)

    return output_df


######################################################

if __name__ == '__main__':
    print('Running cleaning_skus as a main file.')
    df = sku_header_detail_combination('csv/workshop_skus_alltrans.csv', 'csv/SKU_header.csv', 'csv/SKU_detail.csv')
