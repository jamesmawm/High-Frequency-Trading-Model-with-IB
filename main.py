from ib_insync import Forex

from models.hft_model import HftModel

if __name__ == '__main__':
	model = HftModel(
		host='127.0.0.1',
		port=7497,
		client_id=1,
	)

	to_trade = [
		('EURUSD', Forex('EURUSD')),
		('USDJPY', Forex('USDJPY'))
	]

	model.run(to_trade=to_trade, trade_qty=100)

# from ib_insync import *

# util.startLoop()

# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=15)

# contracts = [Forex(pair) for pair in ('EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD')]
# ib.qualifyContracts(*contracts)
#
# eurusd = contracts[0]
#
# for contract in contracts:
# 	ib.reqMktData(contract, '', False, False)
#
# ticker = ib.ticker(eurusd)
# ib.sleep(2)

# eurusd = Forex('EURUSD')
# ticker = ib.reqTickByTickData(eurusd, 'BidAsk')
# while True:
# 	print(ticker)
# 	ib.sleep(2)
#
# print(ticker)

# from ib_insync import *
#
# # util.startLoop()  # uncomment this line when in a notebook
#
# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=1)
#
# contract = Forex('EURUSD')
# bars = ib.reqHistoricalData(contract, endDateTime='', durationStr='30 D',
# 							barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)
# print(bars)
# # convert to pandas dataframe:
# df = util.df(bars)
# print(df[['date', 'open', 'high', 'low', 'close']])

# from tmp_hft_model import HFTModel
#
# if __name__ == "__main__":
#     model = HFTModel(host = 'localhost',
#                      # port = 4002,
#                      port = 7497,
#                      client_id = 1,
#                      is_use_gateway = False,
#                      evaluation_time_secs = 15,
#                      resample_interval_secs = '30s')
# 	model.run()
#
#     # model.start(["RDS A", "BP"], 250)
#     # model.start(["JPM", "BAC"], 100)
#     model.start(["SPY", "QQQ"], 100)
#
