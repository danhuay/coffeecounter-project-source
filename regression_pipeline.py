import matplotlib.pyplot as plt

def linear_regression(df_x, df_y, savefig=True):
    '''
    Taking one dimensional x and one dimensional y, fit a linear regression model.
    :param df_x: pandas series variable x
    :param df_y: pandas series variale y
    :param savefig: if true, a picture will be saved.
    :return: the linear regression model.
    '''
    from sklearn import linear_model
    from sklearn.metrics import mean_squared_error, r2_score

    lr = linear_model.LinearRegression()
    X = df_x.values.reshape(-1, 1)
    y = df_y

    lr.fit(X, y)
    predictions = lr.predict(X)
    print('Coefficients: \n', lr.coef_)
    print('Intercept: \n', lr.intercept_)
    print("MSE: ", mean_squared_error(y, predictions))
    print('Variance score: ', r2_score(y, predictions))

    fig = plt.figure(figsize=(4, 4))
    plt.scatter(X, y, label='Acutal')
    plt.plot(X, predictions, color='orange', label='Prediction')
    plt.xlabel('Time')
    plt.ylabel('Customers')
    plt.legend()

    if savefig:
        plt.tick_params(
            labelleft='off',  # ticks along the top edge are off
            labelbottom='off')  # labels along the bottom edge are off
        fig.savefig('img/reg.png', format='png', bbox_inches='tight', transparent=True, dpi=300)

    plt.show()

    return lr


def forecast_b2b(year, reg1, reg2):
    '''
    year: the year you want to predict
    reg1: year to customer numbers regressor
    reg2: customer numbers to monthly sales regressor
    return: forecast sales break down in months.
    '''
    start_month = (year - 2015) * 12 + 1
    months = np.linspace(start_month, start_month + 11, 12).reshape(-1, 1)
    predicted_customers = reg1.predict(months).reshape(-1, 1)
    for customer in predicted_customers:
        print(customer)
    monthly_sales_of_year = reg2.predict(predicted_customers)

    df = pd.DataFrame(monthly_sales_of_year, columns=['monthly_sales_forecast'])
    idx = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['month'] = idx

    return df
