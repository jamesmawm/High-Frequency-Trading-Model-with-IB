#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

from ib.ext.Contract import Contract
from ib.ext.Order import Order
import ibDataTypes as DataType


def make_ib_contract(contractTuple):
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_exchange = contractTuple[2]
    newContract.m_currency = contractTuple[3]
    newContract.m_expiry = contractTuple[4]
    newContract.m_strike = contractTuple[5]
    newContract.m_right = contractTuple[6]
    #print 'Contract Values:%s,%s,%s,%s,%s,%s,%s:' % contractTuple
    return newContract

def create_stock_contract(stock):
    contract_tuple = (stock, 'STK', 'SMART', 'USD', '', 0.0, '')
    stock_contract = make_ib_contract(contract_tuple)
    return stock_contract

def create_stock_order(quantity, is_buy, is_market_order=True):
    order = Order()
    order.m_orderType = DataType.ORDER_TYPE_MARKET if is_market_order else DataType.ORDER_TYPE_LIMIT
    order.m_totalQuantity = quantity
    order.m_action = DataType.ORDER_ACTION_BUY if is_buy else DataType.ORDER_ACTION_SELL
    return order