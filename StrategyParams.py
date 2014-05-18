#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

import numpy as np
from datetime import datetime

# Short-term look-back period: 5 minutes
# Long-term look-back period: 1 hour


class StrategyParams():
    current_st_beta = 1
    current_lt_beta = 1
    lt_corr = None
    st_corr = None
    st_betas = None
    lt_betas = None

    def __init__(self):
        self.bootstrap_completed = False
        self.stdevs_series = []
        self.last_evaluation_time = datetime.now()
        self.last_stdevs = None
        self.last_lt_stdevs = None

    def set_betas(self, st_betas, lt_betas):
        self.st_betas = st_betas
        self.lt_betas = lt_betas

        self.current_st_beta = st_betas[-1]
        self.current_lt_beta = lt_betas[-1]

    def set_st_betas(self, st_betas):
        self.st_betas = st_betas
        print "Old beta: ", self.current_st_beta
        self.current_st_beta = st_betas[-1]
        print "New beta: ", self.current_st_beta

    def set_bootstrap_completed(self):
        self.bootstrap_completed = True
        self.set_new_evaluation_time()

    def is_evaluation_time_elapsed(self, seconds_diff):
        seconds_elapsed = (datetime.now() - self.last_evaluation_time).seconds
        return seconds_elapsed > seconds_diff

    def set_new_evaluation_time(self):
        self.last_evaluation_time = datetime.now()

    def is_bootstrap_completed(self):
        return self.bootstrap_completed

    def set_corrs(self, st_corr, lt_corr):
        self.lt_corr = lt_corr
        self.st_corr = st_corr

    def get_lt_beta_at_index(self, index):
        return self.lt_betas[index]

    def get_st_beta_at_index(self, index):
        return self.st_betas[index]

    def get_lt_beta(self):
        return self.current_lt_beta

    def get_st_beta(self):
        return self.current_st_beta

    def get_st_corr(self):
        return self.st_corr

    def add_to_stdevs_series(self, stdevs, length):
        self.last_stdevs = stdevs

        if len(self.stdevs_series) == 0:
            for std_value in stdevs:
                self.stdevs_series.append(np.array([std_value]))
        else:
            for i, std_value in enumerate(stdevs):
                series = self.stdevs_series[i]
                series_length = len(series)
                if series_length < length:
                    series = np.hstack((series, std_value))
                    if (series_length+1) < length:
                        padding = np.zeros(max(0,length-series_length-1))
                        series = np.hstack((padding, series))
                else:
                    series[-1] = std_value

                self.stdevs_series[i] = series

    def get_last_stdevs(self):
        return self.last_stdevs

    # TODO: delete this unused function.
    #def trim_stdevs_series_to_length(self, max_length):
    #    for i, stdev_series in enumerate(self.stdevs_series):
    #        if len(stdev_series) > max_length:
    #            self.stdevs_series[i] = stdev_series[-max_length:]

    def get_stdevs_series(self):
        return self.stdevs_series