import pandas as pd
from ib.opt import ibConnection, message as ib_message_type
from ib.opt import Connection
import datetime as dt
import time
from classes.ib_util import IBUtil
from classes.stock_data import StockData
import params.ib_data_types as datatype
from params.strategy_parameters import StrategyParameters
from classes.chart import Chart
import threading
import sys


class HFTModel:

    def __init__(self, host='localhost', port=4001,
                 client_id=101, is_use_gateway=False, evaluation_time_secs=20,
                 resample_interval_secs='30s',
                 moving_window_period=dt.timedelta(hours=1)):
        self.moving_window_period = moving_window_period
        self.chart = Chart()
        self.ib_util = IBUtil()

        # Store parameters for this model
        self.strategy_params = StrategyParameters(evaluation_time_secs,
                                                  resample_interval_secs)

        self.stocks_data = {}  # Dictionary storing StockData objects.
        self.symbols = None  # List of current symbols
        self.account_code = ""
        self.prices = None  # Store last prices in a DataFrame
        self.trade_qty = 0
        self.order_id = 0
        self.lock = threading.Lock()

        # Use ibConnection() for TWS, or create connection for API Gateway
        self.conn = ibConnection() if is_use_gateway else \
            Connection.create(host=host, port=port, clientId=client_id)
        self.__register_data_handlers(self.__on_tick_event,
                                      self.__event_handler)

    def start(self, symbols, trade_qty):
        print "HFT model started."

        self.trade_qty = trade_qty

        self.conn.connect()  # Get IB connection object
        self.__init_stocks_data(symbols)
        self.__request_streaming_data(self.conn)

        print "Bootstrapping the model..."
        start_time = time.time()
        self.__request_historical_data(self.conn)
        self.__wait_for_download_completion()
        self.strategy_params.set_bootstrap_completed()
        self.__print_elapsed_time(start_time)

        print "Calculating strategy parameters..."
        start_time = time.time()
        self.__calculate_strategy_params()
        self.__print_elapsed_time(start_time)

        print "Trading started."
        try:
            self.__update_charts()
            while True:
                time.sleep(1)

        except Exception, e:
            print "Exception:", e
            print "Cancelling...",
            self.__cancel_market_data_request()

            print "Disconnecting..."
            self.conn.disconnect()
            time.sleep(1)

            print "Disconnected."

    def __perform_trade_logic(self):
        """
        This part is the 'secret-sauce' where actual trades takes place.
        My take is that great experience, good portfolio construction,
        and together with robust backtesting will make your strategy viable.
        GOOD PORTFOLIO CONTRUCTION CAN SAVE YOU FROM BAD RESEARCH,
        BUT BAD PORTFOLIO CONSTRUCTION CANNOT SAVE YOU FROM GREAT RESEARCH

        This trade logic uses volatility ratio and beta as our indicators.
        - volatility ratio > 1 :: uptrend, volatility ratio < 1 :: downtrend
        - beta is calculated as: mean(price A) / mean(price B)
        We use the assumption that prive levels will mean-revert.
        Expected price A = beta x price B

        Consider other methods of identifying our trade logic:
        - current trend
        - current regime
        - detect structural breaks
        """
        volatility_ratio = self.strategy_params.get_volatility_ratio()
        is_up_trend, is_down_trend = volatility_ratio > 1, volatility_ratio < 1
        is_overbought, is_oversold = self.__is_overbought_or_oversold()

        # Our final trade signals
        is_buy_signal, is_sell_signal = (is_up_trend and is_oversold), \
                                        (is_down_trend and is_overbought)

        # Use account position details
        symbol_a = self.symbols[0]
        position = self.stocks_data[symbol_a].position
        is_position_closed, is_short, is_long = \
            (position == 0), (position < 0), (position > 0)

        upnl, rpnl = self.__calculate_pnls()

        # Display to terminal dynamically
        signal_text = \
            "BUY" if is_buy_signal else "SELL" if is_sell_signal else "NONE"
        console_output = '\r[%s] signal=%s, position=%s UPnL=%s RPnL=%s\r' % \
            (dt.datetime.now(), signal_text, position, upnl, rpnl)
        sys.stdout.write(console_output)
        sys.stdout.flush()

        if is_position_closed and is_sell_signal:
            print "=================================="
            print "OPEN SHORT POSIITON: SELL A BUY B"
            print "=================================="
            self.__place_spread_order(-self.trade_qty)

        elif is_position_closed and is_buy_signal:
            print "=================================="
            print "OPEN LONG POSIITON: BUY A SELL B"
            print "=================================="
            self.__place_spread_order(self.trade_qty)

        elif is_short and is_buy_signal:
            print "=================================="
            print "CLOSE SHORT POSITION: BUY A SELL B"
            print "=================================="
            self.__place_spread_order(self.trade_qty)

        elif is_long and is_sell_signal:
            print "=================================="
            print "CLOSE LONG POSITION: SELL A BUY B"
            print "=================================="
            self.__place_spread_order(-self.trade_qty)

    def __recalculate_strategy_parameters_at_interval(self):
        """
        Consider re-evaluation of parameters on:
        - regime shifts
        - structural breaks
        """
        if self.strategy_params.is_evaluation_time_elapsed():
            self.__calculate_strategy_params()
            self.strategy_params.set_new_evaluation_time()
            print '[%s] === Beta re-evaluated ===' % dt.datetime.now()

    def __calculate_strategy_params(self):
        """
        Here, we are calculating beta and volatility ratio
        for our signal indicators.

        Consider calculating other statistics here:
        - stddevs of errs
        - correlations
        - co-integration
        """
        [symbol_a, symbol_b] = self.symbols

        filled_prices = self.prices.fillna(method='ffill')
        resampled = filled_prices.resample(
            self.strategy_params.resample_interval_secs, fill_method='ffill')\
            .dropna()
        mean = resampled.mean()
        beta = mean[symbol_a] / mean[symbol_b]

        stddevs = resampled.pct_change().dropna().std()
        volatility_ratio = stddevs[symbol_a] / stddevs[symbol_b]

        self.strategy_params.add_indicators(beta, volatility_ratio)

    def __register_data_handlers(self,
                                 tick_event_handler,
                                 universal_event_handler):
        self.conn.registerAll(universal_event_handler)
        self.conn.unregister(universal_event_handler,
                             ib_message_type.tickSize,
                             ib_message_type.tickPrice,
                             ib_message_type.tickString,
                             ib_message_type.tickGeneric,
                             ib_message_type.tickOptionComputation)
        self.conn.register(tick_event_handler,
                           ib_message_type.tickPrice,
                           ib_message_type.tickSize)

    def __init_stocks_data(self, symbols):
        self.symbols = symbols
        self.prices = pd.DataFrame(columns=symbols)  # Init price storage

        for stock_symbol in symbols:
            contract = self.ib_util.create_stock_contract(stock_symbol)
            self.stocks_data[stock_symbol] = StockData(contract)

    def __request_streaming_data(self, ib_conn):
        # Stream market data
        for index, (key, stock_data) in enumerate(
                self.stocks_data.iteritems()):
            ib_conn.reqMktData(index,
                               stock_data.contract,
                               datatype.GENERIC_TICKS_NONE,
                               datatype.SNAPSHOT_NONE)
            time.sleep(1)

        # Stream account updates
        ib_conn.reqAccountUpdates(True, self.account_code)

    def __request_historical_data(self, ib_conn):
        self.lock.acquire()
        try:
            for index, (key, stock_data) in enumerate(
                    self.stocks_data.iteritems()):
                stock_data.is_storing_data = True
                ib_conn.reqHistoricalData(
                    index,
                    stock_data.contract,
                    time.strftime(datatype.DATE_TIME_FORMAT),
                    datatype.DURATION_1_HR,
                    datatype.BAR_SIZE_5_SEC,
                    datatype.WHAT_TO_SHOW_TRADES,
                    datatype.RTH_ALL,
                    datatype.DATEFORMAT_STRING)
                time.sleep(1)
        finally:
            self.lock.release()

    def __wait_for_download_completion(self):
        is_waiting = True
        while is_waiting:
            is_waiting = False

            self.lock.acquire()
            try:
                for symbol in self.stocks_data.keys():
                    if self.stocks_data[symbol].is_storing_data:
                        is_waiting = True
            finally:
                self.lock.release()

            if is_waiting:
                time.sleep(1)

    def __place_spread_order(self, qty):
        [symbol_a, symbol_b] = self.symbols
        self.__send_order(symbol_a, qty)
        self.__send_order(symbol_b, -qty)

    def __send_order(self, symbol, qty):
        stock_data = self.stocks_data[symbol]
        order = self.ib_util.create_stock_order(abs(qty), qty > 0)
        self.conn.placeOrder(self.__generate_order_id(),
                             stock_data.contract,
                             order)
        stock_data.add_to_position(qty)

    def __generate_order_id(self):
        next_order_id = self.order_id
        self.order_id += 1
        return next_order_id

    def __is_overbought_or_oversold(self):
        [symbol_a, symbol_b] = self.symbols
        leg_a_last_price = self.prices[symbol_a].values[-1]
        leg_b_last_price = self.prices[symbol_b].values[-1]

        expected_leg_a_price = \
            leg_b_last_price * self.strategy_params.get_beta()

        is_overbought = \
            leg_a_last_price < expected_leg_a_price  # Cheaper than expected
        is_oversold = \
            leg_a_last_price > expected_leg_a_price  # Higher than expected

        return is_overbought, is_oversold

    def __on_portfolio_update(self, msg):
        for key, stock_data in self.stocks_data.iteritems():
            if stock_data.contract.m_symbol == msg.contract.m_symbol:
                stock_data.update_position(msg.position,
                                           msg.marketPrice,
                                           msg.marketValue,
                                           msg.averageCost,
                                           msg.unrealizedPNL,
                                           msg.realizedPNL,
                                           msg.accountName)
                return

    def __calculate_pnls(self):
        upnl, rpnl = 0, 0
        for key, stock_data in self.stocks_data.iteritems():
            upnl += stock_data.unrealized_pnl
            rpnl += stock_data.realized_pnl
        return upnl, rpnl

    def __event_handler(self, msg):
        if msg.typeName == datatype.MSG_TYPE_HISTORICAL_DATA:
            self.__on_historical_data(msg)

        elif msg.typeName == datatype.MSG_TYPE_UPDATE_PORTFOLIO:
            self.__on_portfolio_update(msg)

        elif msg.typeName == datatype.MSG_TYPE_MANAGED_ACCOUNTS:
            self.account_code = msg.accountsList

        elif msg.typeName == datatype.MSG_TYPE_NEXT_ORDER_ID:
            self.order_id = msg.orderId

        else:
            print msg

    def __on_historical_data(self, msg):
        print msg

        ticker_index = msg.reqId

        if msg.WAP == -1:
            self.__on_historical_data_completed(ticker_index)
        else:
            self.__add_historical_data(ticker_index, msg)

    def __on_historical_data_completed(self, ticker_index):
        self.lock.acquire()
        try:
            symbol = self.symbols[ticker_index]
            self.stocks_data[symbol].is_storing_data = False
        finally:
            self.lock.release()

    def __add_historical_data(self, ticker_index, msg):
        timestamp = dt.datetime.strptime(msg.date, datatype.DATE_TIME_FORMAT)
        self.__add_market_data(ticker_index, timestamp, msg.close)

    def __on_tick_event(self, msg):
        ticker_id = msg.tickerId
        field_type = msg.field

        # Store information from last traded price
        if field_type == datatype.FIELD_LAST_PRICE:
            last_price = msg.price
            self.__add_market_data(ticker_id, dt.datetime.now(), last_price)
            self.__trim_data_series()

        # Post-bootstrap - make trading decisions
        if self.strategy_params.is_bootstrap_completed():
            self.__recalculate_strategy_parameters_at_interval()
            self.__perform_trade_logic()
            self.__update_charts()

    def __add_market_data(self, ticker_index, timestamp, price):
        symbol = self.symbols[ticker_index]
        self.prices.loc[timestamp, symbol] = float(price)
        self.prices = self.prices.fillna(method='ffill')  # Clear NaN values
        self.prices.sort_index(inplace=True)

    def __update_charts(self):
        if len(self.prices) > 0 and len(self.strategy_params.indicators) > 0:
            self.chart.display_chart(self.prices,
                                     self.strategy_params.indicators)

    def __trim_data_series(self):
        cutoff_timestamp = dt.datetime.now() - self.moving_window_period
        self.prices = self.prices[self.prices.index >= cutoff_timestamp]
        self.strategy_params.trim_indicators_series(cutoff_timestamp)

    @staticmethod
    def __print_elapsed_time(start_time):
        elapsed_time = time.time() - start_time
        print "Completed in %.3f seconds." % elapsed_time

    def __cancel_market_data_request(self):
        for i, symbol in enumerate(self.symbols):
            self.conn.cancelMktData(i)
            time.sleep(1)

