import datetime as dt
import time

import pandas as pd
from ib_insync import IB, Stock, Forex, MarketOrder

from util import order_util, dt_util


class HftModel(object):

	def __init__(self, host='127.0.0.1', port=7497, client_id=1):
		self.host = host
		self.port = port
		self.client_id = client_id

		self.ib = IB()
		self.symbol_map = {}  # maps contract -> symbol
		self.df_hist = None  # stores mid prices in a pandas DataFrame
		self.positions = {}  # stores IB Position object by symbol
		self.pnl = None  # stores IB PnL object
		self.pending_order_ids = set()
		self.is_orders_pending = False

		# Input params
		self.trade_qty = 0
		self.symbols, self.contracts = [], []

		# Strategy params
		self.volatility_ratio = 1
		self.beta = 0
		self.moving_window_period = dt.timedelta(hours=1)
		self.is_buy_signal, self.is_sell_signal = False, False

	def run(self, to_trade=[], trade_qty=0):
		"""
		Entry point that loops forever
		:param to_trade:
		:param trade_qty:
		"""
		# Initialize model based on inputs
		self.trade_qty = trade_qty
		self.symbol_map = {str(contract): ident for (ident, contract) in to_trade}
		self.contracts = [contract for (_, contract) in to_trade]
		self.symbols = list(self.symbol_map.values())
		self.df_hist = pd.DataFrame(columns=self.symbols)

		# Establish connection to IB
		self.ib.connect(self.host, self.port, clientId=self.client_id)
		self.request_account_updates()
		self.request_historical_data()
		self.request_market_data()

		while self.ib.waitOnUpdate():
			self.ib.sleep(1)
			self.recalculate_strategy_params()

	def request_account_updates(self):
		account = self.ib.managedAccounts()[0]
		self.ib.reqPnL(account)
		self.ib.pnlEvent += self.on_pnl

		self.ib.reqPositions()
		self.ib.positionEvent += self.on_position

	def on_account(self, data):
		print('on_acocunt:', data)

	def request_market_data(self):
		for contract in self.contracts:
			self.ib.reqMktData(contract)

		self.ib.pendingTickersEvent += self.on_tick

	def on_tick(self, tickers):
		for ticker in tickers:
			self.get_incoming_tick_data(ticker)

		self.perform_trade_logic()

	def perform_trade_logic(self):
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
		self.calculate_signals()

		if self.is_orders_pending or self.check_and_enter_orders():
			return  # Do nothing while waiting for orders to be filled

		if self.is_position_flat:
			self.print_strategy_params()
		else:
			self.print_account()

	def print_account(self):
		[symbol_a, symbol_b] = self.symbols
		position_a, position_b = self.positions.get(symbol_a), self.positions.get(symbol_b)

		print('[account]{symbol_a} pos={pos_a} avgPrice={avg_price_a}|'
			  '{symbol_b} pos={pos_b}|rpnl={rpnl:.2f} upnl={upnl:.2f}|beta:{beta:.2f} volatility:{vr:.2f}'.format(
			symbol_a=symbol_a,
			pos_a=position_a.position if position_a else 0,
			avg_price_a=position_a.avgCost if position_a else 0,
			symbol_b=symbol_b,
			pos_b=position_b.position if position_b else 0,
			avg_price_b=position_b.avgCost if position_b else 0,
			rpnl=self.pnl.realizedPnL,
			upnl=self.pnl.unrealizedPnL,
			beta=self.beta,
			vr=self.volatility_ratio,
		))

	def print_strategy_params(self):
		print('[strategy params]beta:{beta:.2f} volatility:{vr:.2f}|rpnl={rpnl:.2f}'.format(
			beta=self.beta,
			vr=self.volatility_ratio,
			rpnl=self.pnl.realizedPnL,
		))

	def check_and_enter_orders(self):
		if self.is_position_flat and self.is_sell_signal:
			print('*** OPENING SHORT POSITION ***')
			self.place_spread_order(-self.trade_qty)
			return True

		if self.is_position_flat and self.is_buy_signal:
			print('*** OPENING LONG POSITION ***')
			self.place_spread_order(self.trade_qty)
			return True

		if self.is_position_short and self.is_buy_signal:
			print('*** CLOSING SHORT POSITION ***')
			self.place_spread_order(self.trade_qty)
			return True

		if self.is_position_long and self.is_sell_signal:
			print('*** CLOSING LONG POSITION ***')
			self.place_spread_order(-self.trade_qty)
			return True

		return False

	def place_spread_order(self, qty):
		print('Placing spread orders...')

		[contract_a, contract_b] = self.contracts

		order_a = MarketOrder(order_util.get_order_action(qty), abs(qty))
		trade_a = self.ib.placeOrder(contract_a, order_a)
		print('Order placed:', trade_a)

		order_b = MarketOrder(order_util.get_order_action(-qty), abs(qty))
		trade_b = self.ib.placeOrder(contract_b, order_b)
		print('Order placed:', trade_b)

		self.is_orders_pending = True

		trade_a.filledEvent += self.on_filled
		trade_b.filledEvent += self.on_filled

		self.pending_order_ids.add(trade_a.order.orderId)
		self.pending_order_ids.add(trade_b.order.orderId)
		print('Order IDs pending execution:', self.pending_order_ids)

	def on_filled(self, trade):
		print('Order filled:', trade)
		self.pending_order_ids.remove(trade.order.orderId)
		print('Order IDs pending execution:', self.pending_order_ids)

		# Update flag when all pending orders are filled
		if not self.pending_order_ids:
			self.is_orders_pending = False

	def recalculate_strategy_params(self):
		"""
		Here, we are calculating beta and volatility ratio
		for our signal indicators.

		Consider calculating other statistics here:
		- stddevs of errs
		- correlations
		- co-integration
		"""
		[symbol_a, symbol_b] = self.symbols

		resampled = self.df_hist.resample('30s').ffill().dropna()
		mean = resampled.mean()
		self.beta = mean[symbol_a] / mean[symbol_b]

		stddevs = resampled.pct_change().dropna().std()
		self.volatility_ratio = stddevs[symbol_a] / stddevs[symbol_b]

	def calculate_signals(self):
		self.trim_historical_data()

		is_up_trend, is_down_trend = self.volatility_ratio > 1, self.volatility_ratio < 1
		is_overbought, is_oversold = self.is_overbought_or_oversold()

		# Our final trade signals
		self.is_buy_signal = is_up_trend and is_oversold
		self.is_sell_signal = is_down_trend and is_overbought

	def trim_historical_data(self):
		cutoff_time = dt.datetime.now(tz=dt_util.LOCAL_TIMEZONE) - self.moving_window_period
		self.df_hist = self.df_hist[self.df_hist.index >= cutoff_time]

	def is_overbought_or_oversold(self):
		[symbol_a, symbol_b] = self.symbols
		last_price_a = self.df_hist[symbol_a].dropna().values[-1]
		last_price_b = self.df_hist[symbol_b].dropna().values[-1]

		expected_last_price_a = last_price_b * self.beta

		is_overbought = last_price_a < expected_last_price_a  # Cheaper than expected
		is_oversold = last_price_a > expected_last_price_a  # Higher than expected

		return is_overbought, is_oversold

	def get_incoming_tick_data(self, ticker):
		symbol = self.get_symbol(ticker.contract)

		dt_obj = dt_util.convert_utc_datetime(ticker.time)
		bid = ticker.bid
		ask = ticker.ask
		mid = (bid + ask) / 2

		self.df_hist.loc[dt_obj, symbol] = mid

	def request_historical_data(self):
		for contract in self.contracts:
			self.set_historical_data(contract)

	def set_historical_data(self, contract):
		symbol = self.get_symbol(contract)

		bars = self.ib.reqHistoricalData(
			contract,
			endDateTime=time.strftime('%Y%m%d %H:%M:%S'),
			durationStr='3600 S',
			barSizeSetting='5 secs',
			whatToShow='MIDPOINT',
			useRTH=True,
			formatDate=1
		)
		for bar in bars:
			dt_obj = dt_util.convert_local_datetime(bar.date)
			self.df_hist.loc[dt_obj, symbol] = bar.close

	def get_symbol(self, contract):
		symbol = self.symbol_map.get(str(contract), None)
		if symbol:
			return symbol

		symbol = ''
		if type(contract) is Forex:
			symbol = contract.localSymbol.replace('.', '')
		elif type(contract) is Stock:
			symbol = contract.symbol

		return symbol if symbol in self.symbols else ''

	def on_pnl(self, pnl):
		self.pnl = pnl

	def on_position(self, position):
		symbol = self.get_symbol(position.contract)
		if symbol not in self.symbols:
			print('[warn]symbol not found for position:', position)
			return

		self.positions[symbol] = position

	@property
	def is_position_flat(self):
		position_obj = self.positions.get(self.symbols[0])
		if not position_obj:
			return True

		return position_obj.position == 0

	@property
	def is_position_short(self):
		position_obj = self.positions.get(self.symbols[0])
		return position_obj and position_obj.position < 0

	@property
	def is_position_long(self):
		position_obj = self.positions.get(self.symbols[0])
		return position_obj and position_obj.position > 0
