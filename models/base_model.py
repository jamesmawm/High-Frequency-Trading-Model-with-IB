from ib_insync import IB, Forex, Stock, MarketOrder

from util import order_util

"""
A base model containing common IB functions. 

For other models to extend and use.
"""


class BaseModel(object):
	def __init__(self, host='127.0.0.1', port=7497, client_id=1):
		self.host = host
		self.port = port
		self.client_id = client_id

		self.__ib = None
		self.pnl = None  # stores IB PnL object
		self.positions = {}  # stores IB Position object by symbol

		self.symbol_map = {}  # maps contract to symbol
		self.symbols, self.contracts = [], []

	def init_model(self, to_trade):
		"""
		Initialize the model given inputs before running.
		Stores the input symbols and contracts that will be used for reading positions.

		:param to_trade: list of a tuple of symbol and contract, Example:
			[('EURUSD', Forex('EURUSD'), ]
		"""
		self.symbol_map = {str(contract): ident for (ident, contract) in to_trade}
		self.contracts = [contract for (_, contract) in to_trade]
		self.symbols = list(self.symbol_map.values())

	def connect_to_ib(self):
		self.ib.connect(self.host, self.port, clientId=self.client_id)

	def request_pnl_updates(self):
		account = self.ib.managedAccounts()[0]
		self.ib.reqPnL(account)
		self.ib.pnlEvent += self.on_pnl

	def on_pnl(self, pnl):
		""" Simply store a copy of the latest PnL whenever where are changes """
		self.pnl = pnl

	def request_position_updates(self):
		self.ib.reqPositions()
		self.ib.positionEvent += self.on_position

	def on_position(self, position):
		""" Simply store a copy of the latest Position object for the provided contract """
		symbol = self.get_symbol(position.contract)
		if symbol not in self.symbols:
			print('[warn]symbol not found for position:', position)
			return

		self.positions[symbol] = position

	def request_all_contracts_data(self, fn_on_tick):
		for contract in self.contracts:
			self.ib.reqMktData(contract)

		self.ib.pendingTickersEvent += fn_on_tick

	def place_market_order(self, contract, qty, fn_on_filled):
		order = MarketOrder(order_util.get_order_action(qty), abs(qty))
		trade = self.ib.placeOrder(contract, order)
		trade.filledEvent += fn_on_filled
		return trade

	def get_symbol(self, contract):
		"""
		Finds the symbol given the contract.

		:param contract: The Contract object
		:return: the symbol given for the specific contract
		"""
		symbol = self.symbol_map.get(str(contract), None)
		if symbol:
			return symbol

		symbol = ''
		if type(contract) is Forex:
			symbol = contract.localSymbol.replace('.', '')
		elif type(contract) is Stock:
			symbol = contract.symbol

		return symbol if symbol in self.symbols else ''

	@property
	def ib(self):
		if not self.__ib:
			self.__ib = IB()

		return self.__ib
