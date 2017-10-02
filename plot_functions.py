import matplotlib.pyplot as plt

def plot_trend_and_relationships(timeseries, x, y, time_locations='columns', xylabels=('x_label', 'y_label'),
                                 savefig = ''):
    '''
    This function plots a timeseries trend with target(y) and potential independent variable
    :param timeseries: pd.series of datetime (should contain month)
    :param x: potential independent variable
    :param y: targeted output, forecast
    :param time_locations: specify time_locations = 'index' if the timeseries series are from the index
    :param xylabels: specify label names of variables x and y
    :param savefig: string, if empty, won't save figures. Other wise use it as file name.
    :return: 2 x 2 plots with time vs. y, time vs. x, x vs. y, and monthly mean of y
    '''

    # Initial Setup
    fig = plt.figure(figsize=(6, 6))
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)
    labels = {'x': xylabels[0],
              'y': xylabels[1]}

    # ax1, trend plot
    ax1.plot(timeseries, y)
    ax1.set_title("Trend")
    ax1.set_ylabel(labels['y'])
    # rotating x_tick labels
    for tick in ax1.get_xticklabels():
        tick.set_rotation(45)

    # ax2, seasonal trend
    from seaborn import barplot
    if time_locations == 'index':
        barplot(x=timeseries.month, y=y, ax=ax2)
    else:
        barplot(x=timeseries.dt.month, y=y, ax=ax2)
    ax2.set_title("Monthly Trend")
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Mean of %s' % labels['y'])

    # ax3, time vs. x
    ax3.plot(timeseries, x)
    ax3.set_title('Time vs. %s' % labels['x'])
    ax3.set_ylabel(labels['x'])
    # rotating x_tick labels
    for tick in ax3.get_xticklabels():
        tick.set_rotation(45)

    # ax4, x vs. y
    ax4.scatter(x, y)
    ax4.set_title('%s vs. %s' % (labels['x'], labels['y']))
    ax4.set_xlabel(labels['x'])
    ax4.set_ylabel(labels['y'])

    for axe in [ax1, ax2, ax3, ax4]:
        if axe == ax4: axe.tick_params(labelbottom='off')
        axe.tick_params(labelleft='off')

    plt.tight_layout()  # solve label overlay problem

    if len(savefig) > 0:
        fig.savefig(savefig, format='png', bbox_inches='tight', transparent=True, dpi = 300)
    plt.show()
