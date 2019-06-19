from ib_insync import Forex

from models.hft_model_1 import HftModel1

if __name__ == '__main__':
	model = HftModel1(
		host='127.0.0.1',
		port=7497,
		client_id=1,
	)

	to_trade = [
		('EURUSD', Forex('EURUSD')),
		('USDJPY', Forex('USDJPY'))
	]

	model.run(to_trade=to_trade, trade_qty=100)
