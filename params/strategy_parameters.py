from datetime import datetime
import pandas as pd
import datetime as dt


class StrategyParameters:

    def __init__(self, evaluation_time_secs, resample_interval_secs):
        self.resample_interval_secs = resample_interval_secs
        self.__evaluation_time_secs = evaluation_time_secs

        self.__bootstrap_completed = True
        self.last_evaluation_time = datetime.now()

        self.__COL_BETA = 'beta'
        self.__COL_VOLATILITY_RATIO = 'volatility_ratio'

        self.indicators = pd.DataFrame(columns=[self.__COL_BETA,
                                                self.__COL_VOLATILITY_RATIO])

    def add_indicators(self, beta, volatility_ratio):
        timestamp = dt.datetime.now()
        self.indicators.loc[timestamp] = [beta, volatility_ratio]
        self.indicators.sort_index(inplace=True)

    def trim_indicators_series(self, cutoff_timestamp):
        self.indicators = self.indicators[
            self.indicators.index >= cutoff_timestamp]

    def get_volatility_ratio(self):
        return self.__get_latest_indicator_value(self.__COL_VOLATILITY_RATIO,
                                                 1)

    def get_beta(self):
        return self.__get_latest_indicator_value(self.__COL_BETA)

    def __get_latest_indicator_value(self, column_name, default_value=0):
        if len(self.indicators) > 0:
            return self.indicators[column_name].values[-1]

        return default_value

    def set_bootstrap_completed(self):
        self.__bootstrap_completed = True
        self.set_new_evaluation_time()

    def is_evaluation_time_elapsed(self):
        seconds_elapsed = (datetime.now() - self.last_evaluation_time).seconds
        return seconds_elapsed > self.__evaluation_time_secs

    def set_new_evaluation_time(self):
        self.last_evaluation_time = datetime.now()

    def is_bootstrap_completed(self):
        return self.__bootstrap_completed