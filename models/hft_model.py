import datetime as dt
from ib_insync import IB, Stock, Forex


class HftModel(object):
	def __init__(
		self,
		host='localhost', port=4001,
		client_id=101, is_use_gateway=False, evaluation_time_secs=20,
		resample_interval_secs='30s',
		moving_window_period=dt.timedelta(hours=1)
	):
		self.ib = IB()

	def start(self, symbols=None, trade_qty=None):
		self.ib.connect('127.0.0.1', 7497, clientId=101)
		# contract = Stock('TSLA', 'SMART', 'USD')
		contract = Forex('EURUSD')
		self.request_market_data(contract)

	def request_market_data(self, contract):
		data = self.ib.reqMktData(contract, '', False, False)
		while True:
			print(data)
			self.ib.sleep(2)

	def request_historical_data(self, contract):
		import datetime
		# from ib_insync import *

		dt = ''
		barsList = []
		while True:
			bars = self.ib.reqHistoricalData(
				contract,
				endDateTime=dt,
				durationStr='10 D',
				barSizeSetting='1 min',
				whatToShow='MIDPOINT',
				useRTH=True,
				formatDate=1)
			print(bars)
			if not bars:
				break
			barsList.append(bars)
			dt = bars[0].date
			print(dt)
		print('done!!')
		print(barsList)
