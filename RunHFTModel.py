#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

import numpy as np
import pandas as pd
from ib.opt import ibConnection, message
from ib.opt import Connection
from datetime import datetime
import time
from time import strftime
import matplotlib.dates as dates
import ChartUtil
from StrategyParams import StrategyParams
from StockData import StockData
from ibUtil import *

conn = None
stocks_data = []
errs_data = []
ticks_data = []
strategy_params = StrategyParams()
bid_price, ask_price, last_price, ticker_id = 0, 0, 0, 0
MAXIMUM_TICKS_WINDOW = 60*5
MAXIMUM_ERRS_WINDOW_IN_TICKS = 100
EVALUATION_TIME_IN_SECONDS = 20

account_code = ""
order_id = 0
A_bid_price, A_ask_price = 0, 0

# This part is the 'secret-sauce' where actual trades takes place.
# My take is that great experience, good portfolio construction, and together with
# robust backtesting will make your strategy viable.
# GOOD PORTFOLIO CONTRUCTION CAN SAVE YOU FROM BAD RESEARCH,
# BUT BAD PORTFOLIO CONSTRUCTION CANNOT SAVE YOU FROM GREAT RESEARCH
# Note: These parameters are unrealistic at the moment.
def perform_trade_logic(fair_prices, std_A):
    global strategy_params, stocks_data, conn, order_id, A_bid_price, A_ask_price

    # Use stock A as point of trade
    # In this example, use stock B as the opposite pair.
    # Otherwise, in normal cases use 'cheaper' of the either opposite pairs.
    stock_A_data = stocks_data[0]
    stock_B_data = stocks_data[1]

    position_A = stock_A_data.get_position()
    lt_stdev = stock_A_data.get_long_term_std()
    st_stdev = stock_A_data.get_short_term_std()
    volatility_ratio = st_stdev / lt_stdev


    is_A_overbought, is_A_oversold = get_is_overbought_or_oversold(fair_prices)

    stock_B_fair_price = fair_prices[1]
    stock_contract_A = stock_A_data.get_stock_contract()
    stock_contract_B = stock_B_data.get_stock_contract()

     # Output details to console.
    print ticker_id,")"\
            , "b/a:", A_bid_price, ",", A_ask_price\
            , "std:", round(std_A, 4)\
            , "stderrs:", strategy_params.get_last_stdevs()\
            , "prices:", fair_prices\
            , "vr:", round(volatility_ratio, 3)\
            , "ovrbght/sld:", "T" if is_A_overbought else "F", "T" if is_A_oversold else "F"\
            , "pos:", position_A

    # TODOs:
    # - Identify mean-reverting regime, trending regime and structural breaks
    if position_A == 0:
        if volatility_ratio < 1.0 and is_A_overbought:
            # Short A Buy B
            print "====================="
            print "TRADE 1: SELL A BUY B"
            print "====================="
            qty = 100
            order_sell_A = create_stock_order(qty, False)
            order_buy_B = create_stock_order(qty, True)
            conn.placeOrder(order_id, stock_contract_A, order_sell_A)
            stock_A_data.on_send_order(-qty)
            order_id += 1
            conn.placeOrder(order_id, stock_contract_B, order_buy_B)
            stock_B_data.on_send_order(qty)
            order_id += 1
        elif volatility_ratio > 1.5 and is_A_oversold:
            print "====================="
            print "TRADE 2: BUY A SELL B"
            print "====================="
            qty = 100
            order_buy_A = create_stock_order(qty, True)
            order_sell_B = create_stock_order(qty, False)
            conn.placeOrder(order_id, stock_contract_A, order_buy_A)
            stock_A_data.on_send_order(qty)
            order_id += 1
            conn.placeOrder(order_id, stock_contract_B, order_sell_B)
            stock_B_data.on_send_order(-qty)
            order_id += 1
    elif position_A < 0:
        # Cover short position in A - Take Profit
        if volatility_ratio > 1.5 and is_A_oversold:
            print "====================="
            print "TRADE 3: BUY A SELL B"
            print "====================="
            qty = 100
            order_buy_A = create_stock_order(qty, True)
            order_sell_B = create_stock_order(qty, False)
            conn.placeOrder(order_id, stock_contract_A, order_buy_A)
            stock_A_data.on_send_order(qty)
            order_id += 1
            conn.placeOrder(order_id, stock_contract_B, order_sell_B)
            stock_B_data.on_send_order(-qty)
            order_id += 1
        # Cover short position in A - Stop Loss
        #if vr > 1.5 and is_A_oversold:
    elif position_A > 0:
        # Cover long position in A - Take Profit
        if volatility_ratio < 1.0 and is_A_overbought:
            print "====================="
            print "TRADE 4: SELL A BUY B"
            print "====================="
            qty = 100
            order_sell_A = create_stock_order(qty, False)
            order_buy_B = create_stock_order(qty, True)
            conn.placeOrder(order_id, stock_contract_A, order_sell_A)
            stock_A_data.on_send_order(-qty)
            order_id += 1
            conn.placeOrder(order_id, stock_contract_B, order_buy_B)
            stock_B_data.on_send_order(qty)
            order_id += 1


def get_is_overbought_or_oversold(fair_prices):
    stock_A_price = fair_prices[0]
    is_A_oversold = True
    is_A_overbought = True
    for fair_price in fair_prices[1:]:
        if fair_price > stock_A_price:
            is_A_overbought = False
        else:
            is_A_oversold = False
    return is_A_overbought, is_A_oversold


def on_tick():
    global bid_price, ask_price, last_price, strategy_params, ticker_id
    global A_bid_price, A_ask_price

    precision = 5
    beta = strategy_params.get_st_beta()
    fair_prices = []
    curr_stdevs = []
    std = 0

    # Get fair prices and standard deviation of errors
    series_length = 0
    for i, stockdata in enumerate(stocks_data):
        price_series = stockdata.get_short_term_prices()

        if price_series is None:
            fair_prices.append(None)
        else:
            series_length = len(price_series)
            most_recent_price = price_series[-1]

            if i==0:
                # The original first time series as point of comparison.
                pd_series = pd.Series(price_series)
                std = pd_series.pct_change().std()*100
                fair_prices.append( round(most_recent_price, precision))
            else:
                fair_price = most_recent_price * beta
                fair_prices.append( round(fair_price, precision))

                original_series = stocks_data[0].get_short_term_prices()
                if original_series is not None:
                    err_series = original_series - price_series * beta
                    pd_err_series = pd.Series(err_series)
                    curr_stdevs.append( round(pd_err_series.std(), precision) )
                else:
                    curr_stdevs.append(None)

    if ticker_id == 0:
        A_bid_price = bid_price
        A_ask_price = ask_price

    strategy_params.add_to_stdevs_series(curr_stdevs, series_length)

    # Re-evaluate strategy params every EVALUATION_TIME_IN_SECONDS
    if (strategy_params.is_evaluation_time_elapsed(EVALUATION_TIME_IN_SECONDS)
        #and std > 0.095
        #and std < 0.11
        ):

        # TODO:
        # - Store historical betas
        # - Re-evaluate on regime shifts
        # - Refine current method: To get new beta, use last price when A's standard deviations are at normal levels

        print "=== Beta re-evaluated === "
        st_means = []
        for stock_data_object in stocks_data:
            st_mean = stock_data_object.get_short_term_prices()[-1]
            st_means.append(st_mean)
        st_betas = [st_means[0]/price for price in st_means]
        strategy_params.set_st_betas(st_betas)
        strategy_params.set_new_evaluation_time()

    if A_bid_price != 0 and A_ask_price != 0:
        perform_trade_logic(fair_prices, std)


def process_historical_data(msg):
    print msg

    vwap = msg.WAP
    stock_index = msg.reqId
    if vwap != -1:
        date_time = msg.date
        #open = msg.open
        #high = msg.high
        close = msg.close
        #volume = msg.volume

        stocks_data[stock_index].add_historical_data_point(close, date_time)
    elif vwap == -1:
        stocks_data[stock_index].set_finished_storing()


def process_portfolio_updates(msg):
    contract = msg.contract
    position = msg.position
    market_price = msg.marketPrice
    market_value = msg.marketValue
    average_cost = msg.averageCost
    unrealized_pnl = msg.unrealizedPNL
    realized_pnl = msg.realizedPNL
    account_name = msg.accountName

    global stocks_data
    for stock_data in stocks_data:
        if stock_data.get_stock_contract() == contract:
            stocks_data.update_position(position, market_price, market_value
                                    , average_cost, unrealized_pnl, realized_pnl
                                    , account_name)


def logger(msg):
    if msg.typeName == DataType.MSG_TYPE_HISTORICAL_DATA:
        process_historical_data(msg)
    elif msg.typeName == DataType.MSG_TYPE_UPDATE_PORTFOLIO:
        process_portfolio_updates(msg)
    elif msg.typeName == DataType.MSG_TYPE_MANAGED_ACCOUNTS:
        global account_code
        account_code = msg.accountsList
    elif msg.typeName == DataType.MSG_TYPE_NEXT_ORDER_ID:
        global order_id
        order_id = msg.orderId
    else:
        print "logger: " , msg


def tick_string_event(msg):
    ticker_id = msg.tickerId
    if msg.tickType == DataType.FIELD_LAST_TIMESTAMP:
        print ticker_id, ": ", "ts: ", msg.value
    else:
        print "notickstring: ", msg


def tick_generic(msg):
    print "gen: ", msg


def append_tick_data_to_series(date_obj, price, tick_series):
    dtnum = dates.date2num(date_obj)
    new_tick = np.array([dtnum, price])
    is_replacement = False

    if tick_series is None:
        tick_series = np.array([new_tick])
    else:
        last_dtnum = tick_series[-1][0]
        dt2 = dates.num2date(last_dtnum)

        # Replace with latest price if within same second.
        if (date_obj.replace(tzinfo=None) - dt2.replace(tzinfo=None)).seconds == 0 and date_obj.second == dt2.second:
            is_replacement = True
            tick_series[-1,1] = price
        else:
            tick_series = np.vstack([tick_series, new_tick])

    return tick_series, is_replacement

# Use previous tick interpolation in creating homogeneous time series
def extend_ticks_on_other_series(stock_index, date_obj):
    global stocks_data
    for i, stock_data in enumerate(stocks_data):
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        tick_series = chart_ds.get_ticks()

        if i != stock_index:
            previous_price = chart_ds.get_most_recent_price()
            tick_series, is_replacement = append_tick_data_to_series(date_obj, previous_price, tick_series)
            chart_ds.set_ticks(tick_series)

        if tick_series is not None and len(tick_series) > MAXIMUM_TICKS_WINDOW:
            tick_series = tick_series[-MAXIMUM_TICKS_WINDOW:]
            chart_ds.set_ticks(tick_series)


def get_tick_series_at_index(stock_index):
    global stocks_data
    stock_data = stocks_data[stock_index]
    if stock_data.get_is_bootstrap_completed():
        # Use real-time data
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        tick_series = chart_ds.get_ticks()
        return tick_series
    else:
         # Use historical data
        global ticks_data
        tick_series = ticks_data[stock_index]
        return tick_series


def append_tick_data(stock_index, date_obj, price):
    global stocks_data

    tick_series = get_tick_series_at_index(stock_index)
    tick_series, is_replacement = append_tick_data_to_series(date_obj, price, tick_series)

    stock_data = stocks_data[stock_index]
    if stock_data.get_is_bootstrap_completed():
         # Use real-time data
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        chart_ds.set_ticks(tick_series)
        if not is_replacement:
            extend_ticks_on_other_series(stock_index, date_obj)
    else:
        # Use historical data
        ticks_data[stock_index] = tick_series


def tick_event(msg):
    global ticks_data, bid_price, ask_price, last_price, ticker_id, strategy_params

    ticker_id = msg.tickerId

    if msg.typeName == DataType.MSG_TYPE_TICK_STRING:
        if msg.tickType == DataType.FIELD_LAST_TIMESTAMP:
            print ticker_id, ": ", " ts: ", msg.value
        return

    if msg.field == DataType.FIELD_BID_PRICE:
        #print ticker_id, ": ", "bid: ", msg.price
        bid_price = msg.price
    elif msg.field == DataType.FIELD_ASK_PRICE:
        #print ticker_id, ": ", "ask: ", msg.price
        ask_price= msg.price
    #elif msg.field == DataType.FIELD_BID_SIZE:
    #    print ticker_id, ": ", "bidvol: ", msg.size
    #elif msg.field == DataType.FIELD_ASK_SIZE:
    #    print ticker_id, ": ", "askvol: ", msg.size
    elif msg.field == DataType.FIELD_LAST_PRICE:
        #print ticker_id, ": ", "last: ", msg.price, "at", datetime.now()
        last_price= msg.price
        append_tick_data(ticker_id, datetime.now(), msg.price)

    if strategy_params.is_bootstrap_completed():
        on_tick()

    #elif msg.field == DataType.FIELD_LAST_SIZE:
    #    print ticker_id, ": ", "lastvol: ", msg.size
    #elif msg.field == DataType.FIELD_HIGH:
    #    print ticker_id, ": ", "h: ", msg.price
    #elif msg.field == DataType.FIELD_LOW:
    #    print ticker_id, ": ", "l: ", msg.price
    #elif msg.field == DataType.FIELD_VOLUME:
    #    print ticker_id, ": ", "vol: ", msg.size
    #elif msg.field == DataType.FIELD_CLOSE_PRICE:
    #    print ticker_id, ": ", "close: ", msg.price
    #else:
    #    print "nomsg: ", msg

    #    # Throw away data to keep the desired time window region
    #    while lastime - xdata[0] > dates.minutes(minutes_in_window):
    #        del xdata[0]
    #        del askdata[0]
    #        del biddata[0]


def plot_stocks(strategy_parameters):
    global stocks_data
    ys = []
    for stock_index, stock_data_object in enumerate(stocks_data):
        chart_data_set = stock_data_object.get_historical_short_term_chart_data_set()
        beta = strategy_params.get_st_beta_at_index(stock_index)
        prices = np.array(chart_data_set.get_prices())
        impv_prices = prices * beta
        ys.append(impv_prices)

    x = chart_data_set.get_dates()
    stdevs = strategy_parameters.get_stdevs_series()
    ChartUtil.setup_plots(x, ys, stdevs)


def update_charts():
    global stocks_data, strategy_params, A_ask_price, A_bid_price
    ys = []
    for stock_index, stock_data in enumerate(stocks_data):
        st_chart_ds = stock_data.get_historical_short_term_chart_data_set()
        beta = strategy_params.get_st_beta_at_index(stock_index)
        prices = st_chart_ds.get_prices()*beta
        ys.append(prices)

    ys2 = strategy_params.get_stdevs_series()
    ChartUtil.update_plot(ys, ys2, A_bid_price, A_ask_price)


def request_historical_data(ibconn, stock_index, stock_contract, duration, bar_size):
    ibconn.reqHistoricalData(stock_index
                                , stock_contract
                                , strftime(DataType.DATE_TIME_FORMAT)
                                , duration
                                , bar_size
                                , DataType.WHAT_TO_SHOW_TRADES
                                , DataType.RTH_ALL
                                , DataType.DATEFORMAT_STRING)
    time.sleep(1)


def setup_stocks_data(stocks):
    global ticks_data, stocks_data, errs_data

    for stock in stocks:
        stock_contract = create_stock_contract(stock)
        stock_data = StockData(stock_contract)

        stocks_data.append(stock_data)
        ticks_data.append(None)
        errs_data.append(None)

    ticks_data = np.array(ticks_data)
    errs_data = np.array(errs_data)


def boot_strap_long_term(conn):
    for stock_index, stock_data_object in enumerate(stocks_data):
        stock_data_object.set_is_storing_long_term()
        stock_contract = stock_data_object.get_stock_contract()
        request_historical_data(conn, stock_index, stock_contract
                                , DataType.DURATION_1_DAY, DataType.BAR_SIZE_1_MIN)


def boot_strap_short_term(conn):
    for stock_index, stock_data in enumerate(stocks_data):
        stock_contract = stock_data.get_stock_contract()
        stock_data.set_is_storing_short_term()

        request_historical_data(conn, stock_index, stock_contract
                                , DataType.DURATION_1_MIN, DataType.BAR_SIZE_1_SEC)


def calculate_params(stocks_data_arr):
    lt_means, st_means = [], []
    lt_log_returns, st_log_returns = [], []

    for stock_data_object in stocks_data_arr:
        lt_mean = stock_data_object.get_long_term_mean()
        st_mean = stock_data_object.get_short_term_mean()
        lt_means.append(lt_mean)
        st_means.append(st_mean)

        lt_prices = stock_data_object.get_long_term_prices()
        st_prices = stock_data_object.get_short_term_prices()
        lt_log_return_series = np.log([price/prev_price for price, prev_price in zip(lt_prices, lt_prices[1:])])
        st_log_return_series = np.log([price/prev_price for price, prev_price in zip(st_prices, st_prices[1:])])

        lt_log_returns.append(lt_log_return_series)
        st_log_returns.append(st_log_return_series)

    lt_betas = [lt_means[0]/price for price in lt_means]
    st_betas = [st_means[0]/price for price in st_means]

    # Correlations
    lt_corrs = []
    base_lt_log_return = lt_log_returns[0]
    for lt_log_return in lt_log_returns[1:]:
        correlation_matrix = np.corrcoef(base_lt_log_return, lt_log_return)
        corr = correlation_matrix[1][0]
        corr_rounded = round(corr * 100, 3)
        lt_corrs.append(corr_rounded)

    st_corrs = []
    base_st_log_return = st_log_returns[0]
    for st_log_return in st_log_returns[1:]:
        correlation_matrix = np.corrcoef(base_st_log_return, st_log_return)
        corr = correlation_matrix[1][0]
        corr_rounded = round(corr * 100, 3)
        st_corrs.append(corr_rounded)

    strategy_params.set_betas(st_betas, lt_betas)
    strategy_params.set_corrs(st_corrs, lt_corrs)


def register_data_handlers():
    global conn
    conn.registerAll(logger)
    conn.unregister(logger
                , message.tickSize
                , message.tickPrice
                , message.tickString
                , message.tickGeneric
                , message.tickOptionComputation)
    #conn.register(tick_string_event, message.tickString)
    conn.register(tick_event, message.tickPrice, message.tickSize)
    #conn.register(tick_generic, message.tickGeneric)


def request_streaming_data(conn):
    for stock_index, stock_data_object in enumerate(stocks_data):
        stock_contract = stock_data_object.get_stock_contract()
        conn.reqMktData(stock_index
                        , stock_contract
                        , DataType.GENERIC_TICKS_NONE
                        , DataType.SNAPSHOT_NONE)
        time.sleep(1)

    conn.reqAccountUpdates(True, account_code)


def wait_for_boot_strap_lt_to_complete():
    is_waiting = True
    while is_waiting:
        is_waiting = False
        for stock_data in stocks_data:
            is_stock_waiting = stock_data.is_waiting_for_storing()
            if is_stock_waiting:
                is_waiting = True

        if is_waiting:
            time.sleep(1)


def wait_for_boot_strap_st_to_complete():
    is_waiting = True
    while is_waiting:
        is_waiting = False
        for stock_data in stocks_data:
            is_stock_waiting = stock_data.is_waiting_for_storing()
            if is_stock_waiting:
                is_waiting = True

        if is_waiting:
            time.sleep(1)


def print_elapsed_time(start_time):
    elapsed_time = time.time() - start_time
    print "Completed in %.3f seconds." % elapsed_time


def truncate_tick_series(tick_series, min_length):
    return tick_series[-min_length:]


def truncate_short_term_ticks_to_length(stocks_data_arr, min_length):
    for i, stock_data in enumerate(stocks_data_arr):
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        tick_series = chart_ds.get_ticks()
        tick_series = truncate_tick_series(tick_series, min_length)
        chart_ds.set_ticks(tick_series)

    return stocks_data_arr


def bridge_historical_and_present_ticks(stocks_data_arr, ticks_data, end_time_obj):
    min_length = 0
    for stock_index, stock_data in enumerate(stocks_data_arr):
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        ticks_series = ticks_data[stock_index]
        most_recent_price = chart_ds.get_most_recent_price()
        most_recent_date = chart_ds.get_most_recent_dt()
        most_recent_dt = dates.num2date(most_recent_date).replace(tzinfo=None)
        seconds_left = (end_time_obj - most_recent_dt).seconds
        stock_data.set_is_storing_short_term()
        for i in range(1, seconds_left+1):
            tick_date = most_recent_date + dates.seconds(i)
            next_tick_date = most_recent_date + dates.seconds(i+1)

            # Find price of tick series with same second
            if ticks_series is not None:

                recent_ticks_data = ticks_series[ticks_series[:,0] >= tick_date]
                if len(recent_ticks_data) != 0:
                    recent_ticks_data = recent_ticks_data[recent_ticks_data[:,0] < next_tick_date]

                if len(recent_ticks_data) != 0:
                    most_recent_price = recent_ticks_data[0][1]

            # Store price as stick
            new_tick = np.array([tick_date, most_recent_price])
            chart_ds.add_tick_with_datetime_tick(new_tick)

        stock_data.set_finished_storing()
        ticks_data[stock_index] = None
        stock_data.set_bootstrap_is_completed()

        length = len(chart_ds.get_ticks())
        if min_length==0 or length < min_length:
            min_length = length

    truncate_short_term_ticks_to_length(stocks_data_arr, min_length)


# For debugging tick data
def print_shapes():
    global stocks_data
    print "============"
    for i, stock_data in enumerate(stocks_data):
        chart_ds = stock_data.get_historical_short_term_chart_data_set()
        price_series = chart_ds.get_ticks()
        print np.shape(price_series)
    print "------------"


def cancel_market_data_request():
    global stocks_data, conn
    for stock_index, stock_data in enumerate(stocks_data):
        conn.cancelMktData(stock_index)
        time.sleep(1)


def main():
    global conn

    print "HFT model started."

    # Use ibConnection() for TWS, or create connection for API Gateway
    #conn = ibConnection()
    conn = Connection.create(port=4001, clientId=101)
    register_data_handlers()
    conn.connect()

     # Input your stocks of interest
    stocks = ("C", "MS")
    setup_stocks_data(stocks)
    request_streaming_data(conn)

    print "Boot strapping..."
    start_time = time.time()
    boot_strap_long_term(conn)
    wait_for_boot_strap_lt_to_complete()
    boot_strap_short_term(conn)
    wait_for_boot_strap_st_to_complete()
    print_elapsed_time(start_time)
    strategy_params.set_bootstrap_completed()

    print "Calculating strategy parameters..."
    start_time = time.time()
    calculate_params(stocks_data)
    print_elapsed_time(start_time)

    print "Bridging historical data..."
    start_time = time.time()
    bridge_historical_and_present_ticks(stocks_data, ticks_data, datetime.now())
    print_elapsed_time(start_time)

    print "Trading started."

    try:
        plot_stocks(strategy_params)

        while True:
            update_charts()
            time.sleep(1)

    except Exception, e:
        print "Cancelling...",
        cancel_market_data_request()

        print "Disconnecting..."
        conn.disconnect()
        time.sleep(1)

        print "Disconnected."

if __name__ == '__main__':
    main()