#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

from datetime import datetime
import ibDataTypes as DataType
import matplotlib.dates as dates
import numpy as np
from matplotlib.dates import date2num
import math


class ChartDataSet:
    def __init__(self):
        self.prices = []
        self.dates = []
        self.most_recent_dt = 0
        self.ticks = None

    def compare_and_store_most_recent_date_time(self, num_dt):
        if num_dt > self.most_recent_dt:
            self.most_recent_dt = num_dt

    def get_datetime_from_string(self, datestr):
        dt = datetime.strptime(datestr, DataType.DATE_TIME_FORMAT)
        return dates.date2num(dt)

    def add_tick_with_datetime_tick(self, tick):
        if self.ticks is None:
            self.ticks = np.array([tick])
        else:
            self.ticks = np.vstack([self.ticks, tick])

    def add_tick(self, price, date):
        dt = self.get_datetime_from_string(date)
        self.prices.append(price)
        self.dates.append(dt)
        self.compare_and_store_most_recent_date_time(dt)

        tick = [dt, price]
        self.add_tick_with_datetime_tick(tick)

    def get_seconds_elapsed_since_time(self, start_time_str):
        dt = datetime.strptime(start_time_str, DataType.DATE_TIME_FORMAT)
        num_dt = date2num(dt)
        elapsed_time = math.floor((num_dt - self.most_recent_dt) * 100000)
        return elapsed_time

    def get_seconds_elapsed_since_time_as_ib_string(self, start_time_str):
        elapsed_time = self.get_seconds_elapsed_since_time(start_time_str)
        ib_string = "%.0f S" % elapsed_time
        return ib_string

    def get_most_recent_dt(self):
        return self.most_recent_dt

    def get_prices(self):
        if self.ticks is None:
            return None

        result = self.ticks[:,1]
        return result

    def get_most_recent_price(self):
        price_series = self.get_prices()
        if price_series is not None:
            return price_series[-1]
        return 0

    def get_dates(self):
        return self.ticks[:,0]

    def get_dates_labels(self):
        return [dates.num2date(dt).strftime(DataType.DATE_TIME_FORMAT) for dt in self.ticks[:,0]]

    def get_ticks(self):
        return self.ticks

    def set_ticks(self, ticks):
        self.ticks = ticks