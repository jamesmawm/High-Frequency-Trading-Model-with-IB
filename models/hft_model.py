import time
import datetime as dt
import pandas as pd
from threading import Thread

from ib_insync import IB, Stock, Forex
from ib_insync.util import df


class HftModel(object):
	def __init__(
		self,
		host='localhost', port=4001,
		client_id=101, is_use_gateway=False, evaluation_time_secs=20,
		resample_interval_secs='30s',
		moving_window_period=dt.timedelta(hours=1)
	):
		self.ib = IB()

	def run(self):
		self.ib.connect('127.0.0.1', 7497, clientId=101)

		eurusd = Forex('EURUSD')
		usdjpy = Forex('USDJPY')
		# ticker = ib.reqTickByTickData(eurusd, 'BidAsk')
		# ticker = ib.reqTickByTickData(usdjpy, 'BidAsk')
		# ib.pendingTickersEvent += self.on_ticker
		dt = ''

		self.hist = self.get_historical_data(eurusd)
		# print(hist)

		self.request_market_data(eurusd)

		# ib.pendingTickersEvent += self.on_ticker

		while self.ib.waitOnUpdate():
			self.ib.sleep(1)

	def request_market_data(self, contract):
		self.ib.reqMktData(contract)
		self.ib.pendingTickersEvent += self.on_tick

	def on_tick(self, tickers):
		for ticker in tickers:
			print(ticker.time, ticker.close)
			dt_obj = pd.to_datetime(ticker.time)
			self.hist.loc[dt_obj] = ticker.close
			# self.hist.index = self.hist.index.tz_convert('Asia/Singapore')
			print(self.hist.tail())

		r = self.hist.resample('MS')
		print(r)


	def get_historical_data(self, contract):
		bars = self.ib.reqHistoricalData(
			contract,
			endDateTime=time.strftime('%Y%m%d %H:%M:%S'),
			durationStr='3600 S',
			barSizeSetting='5 secs',
			whatToShow='MIDPOINT',
			useRTH=True,
			formatDate=1
		)
		# df_obj = df_close(bars)
		df_obj = pd.DataFrame(columns=['datetime', 'last'])
		for bar in bars:
			# dt_obj = dt.datetime.strptime(str(bar.date), '%Y-%m-%d %H:%M:%S')
			dt_obj = pd.to_datetime(bar.date, format='%Y-%m-%d %H:%M:%s')
			df_obj['datetime'] = dt_obj
			df_obj['last'] = bar.close
		#
		# df_close = pd.DataFrame(columns=['close'])
		# df_close.loc[df.index, 'close'] = df.close
		df_obj = df_obj.set_index('datetime')
		print(df_obj.head())
		return df_obj

	def on_ticker(self, ticker):
		print('tiker:', ticker)
