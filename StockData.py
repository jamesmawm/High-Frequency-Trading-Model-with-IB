#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

from ChartDataSet import ChartDataSet
import pandas as pd


class StockData:
    is_storing_long_term = False
    is_storing_short_term = False
    is_bootstrap_completed = False

    def __init__(self, contract):
        self.contract = contract
        self.historical_lt_chart_data_set = ChartDataSet()
        self.historical_st_chart_data_set = ChartDataSet()
        self.position = 0
        self.market_price = 0
        self.market_value = 0
        self.average_cost = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.account_name = ""
        self.is_order_filled = False

    def set_bootstrap_is_completed(self):
        self.is_bootstrap_completed = True

    def get_is_bootstrap_completed(self):
        return self.is_bootstrap_completed

    def get_stock_contract(self):
        return self.contract

    def set_is_storing_long_term(self):
        self.is_storing_long_term = True

    def set_is_storing_short_term(self):
        self.is_storing_short_term = True

    def set_finished_storing(self):
        self.is_storing_long_term = False
        self.is_storing_short_term = False

    def is_waiting_for_storing(self):
        return self.is_storing_long_term or self.is_storing_short_term

    def add_historical_data_point(self, price, date):
        if self.is_storing_long_term:
            self.historical_lt_chart_data_set.add_tick(price, date)
        elif self.is_storing_short_term:
            self.historical_st_chart_data_set.add_tick(price, date)

    def add_incoming_tick(self, price, date):
        self.historical_st_chart_data_set.add_tick(price, date)

    def get_historical_chart_data_set(self):
        return self.historical_lt_chart_data_set

    def get_historical_short_term_chart_data_set(self):
        return self.historical_st_chart_data_set

    def get_long_term_prices(self):
        return self.historical_lt_chart_data_set.get_prices()

    def get_short_term_prices(self):
        return self.historical_st_chart_data_set.get_prices()

    def get_long_term_mean(self):
        pdseries = pd.Series(self.get_long_term_prices())
        return pdseries.values.mean()

    def get_short_term_mean(self):
        pdseries = pd.Series(self.get_short_term_prices())
        return pdseries.values.mean()

    def get_short_term_std(self):
        return pd.Series(self.get_short_term_prices()).pct_change().std()*100

    def get_long_term_std(self):
        return pd.Series(self.get_long_term_prices()).pct_change().std()*100

    def update_position(self
        , position, market_price, market_value, average_cost, unrealized_pnl, realized_pnl, account_name):
        self.position = position
        self.market_price = market_price
        self.market_value = market_value
        self.average_cost = average_cost
        self.unrealized_pnl = unrealized_pnl
        self.realized_pnl = realized_pnl
        self.account_name = account_name

    def on_send_order(self, position):
        self.position += position
        self.is_order_filled = False

    def get_position(self):
        return self.position