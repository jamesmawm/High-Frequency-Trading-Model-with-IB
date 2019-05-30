
class ContractData:

    def __init__(self, contract):
        self.contract = contract
        self.position = 0
        self.is_storing_data = True
        self.market_price = 0
        self.market_value = 0
        self.average_cost = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.account_name = ""

    def add_to_position(self, position):
        self.position += position

    def update_position(self, position, market_price,
                        market_value, average_cost, unrealized_pnl,
                        realized_pnl, account_name):
        self.position = position
        self.market_price = float(market_price)
        self.market_value = float(market_value)
        self.average_cost = float(average_cost)
        self.unrealized_pnl = float(unrealized_pnl)
        self.realized_pnl = float(realized_pnl)
        self.account_name = account_name