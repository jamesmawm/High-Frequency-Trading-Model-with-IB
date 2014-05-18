#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

import unittest
import RunHFTModel
from datetime import datetime
import numpy as np
import matplotlib.dates as dates
import StrategyParams as strategyparams
from StockData import StockData
from ibUtil import *

class TestStockData(unittest.TestCase):
    stock = "C"

    price_1 = 15.5
    dt_1 = "20140511  19:15:24"

    price_2 = 16.0
    dt_2 = "20140511  19:15:25"

    def setUp(self):
        self.test_contract = create_stock_contract(self.stock)

    def check_array( self, expected, result, digits=3):
        if hasattr(expected,'__iter__'):
            if type(expected)==dict:
                for (key,expectedElem) in expected.iteritems():
                    resElem = result[key]
                    self.check_array(expectedElem, resElem, digits )
            else:
                for (i, expectedElem) in enumerate(expected):
                    resElem = result[i]
                    self.check_array(expectedElem, resElem, digits )
        else:
            if type(expected) is str:
                self.assertEqual(expected, result)
            else:
                self.assertAlmostEqual(expected, result, digits)

    def testAdd1HistoricalData(self):
        test_stock_data = StockData(self.test_contract)
        test_stock_data.set_is_storing_long_term()
        test_stock_data.add_historical_data_point(self.price_1, self.dt_1)
        test_chart_data_set = test_stock_data.get_historical_chart_data_set()

        result_prices = test_chart_data_set.get_prices()
        expected_prices = [self.price_1]

        self.assertEqual(result_prices, expected_prices)

    def testAdd2HistoricalData(self):
        test_stock_data = StockData(self.test_contract)
        test_stock_data.set_is_storing_long_term()
        test_stock_data.add_historical_data_point(self.price_1, self.dt_1)
        test_stock_data.add_historical_data_point(self.price_2, self.dt_2)
        test_chart_data_set = test_stock_data.get_historical_chart_data_set()

        result_prices = test_chart_data_set.get_prices()
        expected_prices = np.array([self.price_1, self.price_2])

        self.check_array(expected_prices, result_prices)

    def testCalculateParamsSTAndLTBetasOn2Stocks(self):
        stocks_data = []

        test_stock_data1 = StockData(create_stock_contract(self.stock))
        test_stock_data1.set_is_storing_long_term()
        test_stock_data1.add_historical_data_point(50, self.dt_1)
        test_stock_data1.add_historical_data_point(60, self.dt_2)
        test_stock_data1.set_finished_storing()
        test_stock_data1.set_is_storing_short_term()
        test_stock_data1.add_historical_data_point(20, self.dt_1)
        test_stock_data1.add_historical_data_point(30, self.dt_2)
        stocks_data.append(test_stock_data1)

        test_stock_data2 = StockData(self.test_contract)
        test_stock_data2.set_is_storing_long_term()
        test_stock_data2.add_historical_data_point(10, self.dt_1)
        test_stock_data2.add_historical_data_point(12, self.dt_2)
        test_stock_data2.set_finished_storing()
        test_stock_data2.set_is_storing_short_term()
        test_stock_data2.add_historical_data_point(40, self.dt_1)
        test_stock_data2.add_historical_data_point(60, self.dt_2)
        stocks_data.append(test_stock_data2)

        RunHFTModel.calculate_params(stocks_data)

    def createSimpleChartDataSetWith2TimePoints(self):
        test_stock_data1 = StockData(create_stock_contract(self.stock))

        test_stock_data1.set_is_storing_long_term()
        test_stock_data1.add_historical_data_point(50, "20140511  19:15:24")
        test_stock_data1.add_historical_data_point(60, "20140511  19:15:25")
        test_stock_data1.set_finished_storing()
        return test_stock_data1

    def testMostRecentTickDateTime(self):
        test_stock_data1 = self.createSimpleChartDataSetWith2TimePoints()
        chart_ds = test_stock_data1.get_historical_chart_data_set()

        result_dt = chart_ds.get_most_recent_dt()
        expected_dt = 735364.8023726852

        self.assertEqual(result_dt, expected_dt)

    def testGet5SecondsLaterTimeSinceMostRecentTickDateTime(self):
        test_stock_data1 = self.createSimpleChartDataSetWith2TimePoints()
        chart_ds = test_stock_data1.get_historical_chart_data_set()

        current_time_str = "20140511  19:15:30"
        elapsed_time = chart_ds.get_seconds_elapsed_since_time(current_time_str)
        expected_result = 5

        self.assertEqual(expected_result, elapsed_time)

    def testGet5SecondsLaterIBTimeString(self):
        test_stock_data1 = self.createSimpleChartDataSetWith2TimePoints()
        chart_ds = test_stock_data1.get_historical_chart_data_set()

        current_time_str = "20140511  19:15:30"
        ib_string = chart_ds.get_seconds_elapsed_since_time_as_ib_string(current_time_str)
        expected_result = "5 S"

        self.assertEqual(expected_result, ib_string)

    def testTicksDataWith3Stocks(self):
        ticks_data = [None, None, None]
        dt1 = datetime.strptime("2014-05-11 19:15:23", DataType.DATE_TIME_FORMAT_LONG)
        dt2 = datetime.strptime("2014-05-11 19:15:24", DataType.DATE_TIME_FORMAT_LONG)

        tick_series = ticks_data[1]
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt1, 20, tick_series)
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt2, 21, tick_series)
        ticks_data[1] = tick_series

        expected = [None, np.array([[  7.35364802e+05,  20],
                            [  7.35364802e+05,   21]]), None]
        self.check_array(expected, ticks_data, 3)

    def testTicksDataWith3StocksInSameSeconds(self):
        ticks_data = [None, None, None]
        dt1 = datetime.strptime("2014-05-11 19:15:23.009", DataType.DATE_TIME_FORMAT_LONG_MILLISECS)
        dt2 = datetime.strptime("2014-05-11 19:15:23.010", DataType.DATE_TIME_FORMAT_LONG_MILLISECS)

        tick_series = ticks_data[1]
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt1, 20, tick_series)
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt2, 21, tick_series)
        ticks_data[1] = tick_series

        expected = [None, np.array([[  7.35364802e+05,   21]]), None]
        self.check_array(expected, ticks_data, 3)

    def testTicksDataWith3StocksInDifferentSeconds(self):
        ticks_data = []
        ticks_data.append(None)
        ticks_data.append(None)
        ticks_data.append(None)

        dt1 = datetime.strptime("2014-05-11 19:15:23.059", DataType.DATE_TIME_FORMAT_LONG_MILLISECS)
        dt2 = datetime.strptime("2014-05-11 19:15:24.010", DataType.DATE_TIME_FORMAT_LONG_MILLISECS)
        tick_series = ticks_data[1]
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt1, 20, tick_series)
        tick_series, is_replacement = RunHFTModel.append_tick_data_to_series(dt2, 21, tick_series)
        ticks_data[1] = tick_series

        expected = [None, np.array([[735364.80235, 20], [735364.802361,   21]]), None]
        self.check_array(expected, ticks_data, 3)

    def testBridgeBootstrap(self):
        # Store historical ticks
        test_stock_data1 = StockData(create_stock_contract(self.stock))
        test_stock_data1.set_is_storing_short_term()
        test_stock_data1.add_historical_data_point(50, "20140511  19:15:24")
        test_stock_data1.add_historical_data_point(60, "20140511  19:15:25")
        test_stock_data1.set_finished_storing()

        stocks_data = [test_stock_data1]

        # Store incoming ticks
        p1 = 20
        p2 = 21
        p3 = 22
        p4 = 23
        p5 = 24

        dt1 = datetime.strptime("2014-05-11 19:15:23", DataType.DATE_TIME_FORMAT_LONG)
        dt2 = datetime.strptime("2014-05-11 19:15:24", DataType.DATE_TIME_FORMAT_LONG)
        dt3 = datetime.strptime("2014-05-11 19:15:25", DataType.DATE_TIME_FORMAT_LONG)
        dt4 = datetime.strptime("2014-05-11 19:15:26", DataType.DATE_TIME_FORMAT_LONG)
        dt5 = datetime.strptime("2014-05-11 19:15:27", DataType.DATE_TIME_FORMAT_LONG)

        tick_1 = np.array([dates.date2num(dt1), p1])
        tick_2 = np.array([dates.date2num(dt2), p2])
        tick_3 = np.array([dates.date2num(dt3), p3])
        tick_4 = np.array([dates.date2num(dt4), p4])
        tick_5 = np.array([dates.date2num(dt5), p5])

        # Create test ticks data.
        tick_series = np.array(tick_1)
        tick_series = np.vstack([tick_series, tick_2])
        tick_series = np.vstack([tick_series, tick_3])
        tick_series = np.vstack([tick_series, tick_4])
        tick_series = np.vstack([tick_series, tick_5])
        ticks_data = [tick_series]

        # Bridge ticks and retrieve results
        end_time = datetime.strptime("2014-05-11 19:15:35", DataType.DATE_TIME_FORMAT_LONG)
        RunHFTModel.bridge_historical_and_present_ticks(stocks_data, ticks_data, end_time)
        chart_ds = stocks_data[0].get_historical_short_term_chart_data_set()

        # Test for prices
        result_prices = chart_ds.get_prices()
        expected_prices = [50, 60, 23, 24,
                           24, 24, 24, 24,
                           24, 24, 24, 24]

        self.check_array(expected_prices, result_prices)
        # Test date labels
        expected_datelabels = ['20140511 19:15:24'
                                , '20140511 19:15:25'
                                , '20140511 19:15:26'
                                , '20140511 19:15:27'
                                , '20140511 19:15:28'
                                , '20140511 19:15:29'
                                , '20140511 19:15:30'
                                , '20140511 19:15:31'
                                , '20140511 19:15:32'
                                , '20140511 19:15:33'
                                , '20140511 19:15:34'
                                , '20140511 19:15:35'
                                ]
        result_datelabels = chart_ds.get_dates_labels()
        self.check_array(expected_datelabels, result_datelabels)

    def testStandardDeviationOnHistoricalShortTermData(self):
        test_stock_data1 = StockData(create_stock_contract(self.stock))
        test_stock_data1.set_is_storing_short_term()
        test_stock_data1.add_historical_data_point(50, "20140511  19:15:24")
        test_stock_data1.add_historical_data_point(60, "20140511  19:15:25")
        test_stock_data1.add_historical_data_point(70, "20140511  19:15:26")
        test_stock_data1.add_historical_data_point(80, "20140511  19:15:27")
        test_stock_data1.add_historical_data_point(90, "20140511  19:15:28")
        test_stock_data1.add_historical_data_point(110, "20140511  19:15:29")
        test_stock_data1.set_finished_storing()

        stdev = test_stock_data1.get_short_term_std()
        expected = 0.039971566 * 100

        self.assertAlmostEqual(expected, stdev, 5)

    def testTruncateTickSeries(self):
        test_stock_data1 = StockData(create_stock_contract(self.stock))
        test_stock_data1.set_is_storing_short_term()
        test_stock_data1.add_historical_data_point(50, "20140511  19:15:24")
        test_stock_data1.add_historical_data_point(60, "20140511  19:15:25")
        test_stock_data1.add_historical_data_point(70, "20140511  19:15:26")
        test_stock_data1.add_historical_data_point(80, "20140511  19:15:27")
        test_stock_data1.add_historical_data_point(90, "20140511  19:15:28")
        test_stock_data1.add_historical_data_point(100, "20140511  19:15:29")
        test_stock_data1.set_finished_storing()

        length = 5
        chart_ds = test_stock_data1.get_historical_short_term_chart_data_set()
        tick_series = chart_ds.get_prices()
        new_tick_series = RunHFTModel.truncate_tick_series(tick_series, length)

        expected = [60, 70, 80, 90, 100]
        self.check_array(expected, new_tick_series)

    def testAddStdevToStrategy(self):
        strategy_params = strategyparams.StrategyParams()
        strategy_params.add_to_stdevs_series([1, 10], 1)
        strategy_params.add_to_stdevs_series([2, 20], 2)
        strategy_params.add_to_stdevs_series([3, 30], 3)
        strategy_params.add_to_stdevs_series([4, 40], 4)
        strategy_params.add_to_stdevs_series([5, 50], 5)
        strategy_params.add_to_stdevs_series([6, 60], 6)

        expected_series_1 = np.array([1, 2, 3, 4, 5, 6])
        expected_series_2 = np.array([10, 20, 30, 40, 50, 60])
        expected = [expected_series_1, expected_series_2]
        result = strategy_params.get_stdevs_series()

        self.check_array(expected, result)

        #strategy_params.trim_stdevs_series_to_length(3)
        #expected_series_1 = np.array([4, 5, 6])
        #expected_series_2 = np.array([40, 50, 60])
        #expected = [expected_series_1, expected_series_2]
        #result = strategy_params.get_stdevs_series()

    def testAddStdevToStrategyWithPadding(self):
        strategy_params2 = strategyparams.StrategyParams()
        strategy_params2.add_to_stdevs_series([4, 40], 4)
        strategy_params2.add_to_stdevs_series([5, 50], 5)
        strategy_params2.add_to_stdevs_series([6, 60], 6)

        expected_series_1 = np.array([0, 0, 0, 4, 5, 6])
        expected_series_2 = np.array([0, 0, 0, 40, 50, 60])
        expected = [expected_series_1, expected_series_2]
        result = strategy_params2.get_stdevs_series()

        self.check_array(expected, result)

    def testAddStdevToStrategyWithPaddingAndReplacement(self):
        strategy_params2 = strategyparams.StrategyParams()
        strategy_params2.add_to_stdevs_series([4, 40], 4)
        strategy_params2.add_to_stdevs_series([5, 50], 5)
        strategy_params2.add_to_stdevs_series([6, 60], 6)
        strategy_params2.add_to_stdevs_series([7, 70], 6)

        expected_series_1 = np.array([0, 0, 0, 4, 5, 7])
        expected_series_2 = np.array([0, 0, 0, 40, 50, 70])
        expected = [expected_series_1, expected_series_2]
        result = strategy_params2.get_stdevs_series()

        self.check_array(expected, result)

    def testAIsNeitherOverboughtOrOversold(self):
        fairPrices = [50, 60 ,30]
        result = RunHFTModel.get_is_overbought_or_oversold(fairPrices)
        expected = False, False
        self.assertEqual(expected, result)

    def testAIsOverSold(self):
        fairPrices = [50, 60 ,70]
        result = RunHFTModel.get_is_overbought_or_oversold(fairPrices)
        expected = False, True
        self.assertEqual(expected, result)

    def testAIsOverBought(self):
        fairPrices = [50, 40 ,30]
        result = RunHFTModel.get_is_overbought_or_oversold(fairPrices)
        expected = True, False
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
    print "Unit Test Main"