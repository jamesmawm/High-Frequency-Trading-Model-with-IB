import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import threading
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class Chart:

    def __init__(self, precision=5):
        self.precision = precision
        self.axplot = {}
        self.fig = None
        self.lock = threading.Lock()

    def display_chart(self, *args):
        self.lock.acquire()
        try:
            series_list = self.__consolidate_to_series_list(*args)
            self.__check_and_init_plot(series_list)
            self.__update_all_plots(series_list)
            plt.draw()
            plt.pause(0.01)
        finally:
            self.lock.release()

    def __check_and_init_plot(self, series_list):
        if self.fig is None:
            self.__init_plot(series_list)

    def __update_all_plots(self, series_list):
        for series in series_list:
            self.__update_plot(series, series.name)

    def __update_plot(self, series, name):
        if name in self.axplot:
            (axis, plot) = self.axplot[name]

            plot.set_xdata(series.index)
            plot.set_ydata(series.values)

            self.__update_xlim(series, axis)
            self.__update_ylim(series, axis)

            title = '%s: %s' % (name, round(series.values[-1], self.precision))
            axis.set_title(title)

    @staticmethod
    def __consolidate_to_series_list(*args):
        series_list = []
        for df in args:
            for column in df.columns:
                series_list.append(pd.Series(df[column], name=column))

        return series_list

    def __init_plot(self, series_list):
        num_series = len(series_list)
        self.fig = plt.figure(num_series)

        for i, series in enumerate(series_list):
            axis = self.fig.add_subplot(num_series, 1, i+1)
            plot, = axis.plot(series.index, series.values)
            plt.grid()
            self.axplot[series.name] = (axis, plot)

        self.fig.tight_layout()

    def __update_xlim(self, series, axis):
        self.__update_lim(axis, series.index, False)

    def __update_ylim(self, series, axis):
        self.__update_lim(axis, series.values, True)

    def __update_lim(self, axis, values, is_y):
        if len(values) > 1:
            value_low, value_high = min(values), max(values)
            if value_low != value_high:
                self.__set_lim(axis, value_low, value_high, is_y)
                return

        (value_low, value_high) = \
            (0, 1) if is_y else \
            (dt.datetime.now()-dt.timedelta(hours=1), dt.datetime.now())
        self.__set_lim(axis, value_low, value_high, is_y)

    @staticmethod
    def __set_lim(axis, value_low, value_high, is_y):
        if is_y:
            axis.set_ylim(value_low, value_high, auto=True)
        else:
            axis.set_xlim(value_low, value_high, auto=True)