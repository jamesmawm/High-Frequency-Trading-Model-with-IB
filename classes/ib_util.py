from ib.ext.Contract import Contract
from ib.ext.Order import Order
import ib_data_types as DataType


class IBUtil:

    def __init__(self):
        pass

    def create_stock_contract(self, stock):
        contract_tuple = (stock, 'STK', 'SMART', 'USD', '', 0.0, '')
        stock_contract = self.__make_ib_contract(contract_tuple)
        return stock_contract


    def create_stock_order(self, quantity, is_buy, is_market_order=True):
        order = Order()
        order.m_totalQuantity = quantity
        order.m_orderType = \
            DataType.ORDER_TYPE_MARKET if is_market_order else \
            DataType.ORDER_TYPE_LIMIT
        order.m_action = \
            DataType.ORDER_ACTION_BUY if is_buy else \
            DataType.ORDER_ACTION_SELL
        return order

    @staticmethod
    def __make_ib_contract(contract_tuple):
        new_contract = Contract()
        new_contract.m_symbol = contract_tuple[0]
        new_contract.m_secType = contract_tuple[1]
        new_contract.m_exchange = contract_tuple[2]
        new_contract.m_currency = contract_tuple[3]
        new_contract.m_expiry = contract_tuple[4]
        new_contract.m_strike = contract_tuple[5]
        new_contract.m_right = contract_tuple[6]
        return new_contract

    @staticmethod
    def create_generic_contract(symbol, sec_type, exch, prim_exch, curr):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = sec_type
        contract.m_exchange = exch
        contract.m_primaryExch = prim_exch
        contract.m_currency = curr
        return contract

    @staticmethod
    def create_generic_order(order_type, quantity, action):
        order = Order()
        order.m_orderType = order_type
        order.m_totalQuantity = quantity
        order.m_action = action
        return order
