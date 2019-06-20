# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 01:07:51 2019

@author: 43739
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import warnings


# don't need those warnings
warnings.filterwarnings("ignore")

# parameter
os.chdir('C:\\Users\\jloss\\PyCharmProjects\\IB_PairsTrading_Algo\\backtesting\\')
tickers = ['bp', 'rds-a']
# name in variable_name is of no importance, just to nominate some dataframe 
variable_name = ['BP', 'RDSA']
intra_freq = '1min'
year = '2018'

# Import the backtrader platform
import backtrader as bt


class ValueObserver(bt.Observer):
    lines = ('value',)

    plotinfo = dict(plot = True, subplot = True, plotlinelabels = True)

    plotlines = dict(
            # value=dict(marker='*', markersize=8.0, color='lime', fillstyle='full')
            value = dict(linewidth = 1.5)
    )

    def next(self):
        self.lines.value[0] = self._owner.dataclose_x - self._owner.params.m * self._owner.dataclose_y


# Create a Stratey
class PairStrategy(bt.Strategy):
    params = (
            ('m', 0.564),  # slope
            ('b', 5.597244),  # intercept
            ('std', 1.355027),
            ('avg', 0.5),
            ('muti', 1),  # muti*std+avg
            ('size', 1000)
    )


    def log(self, txt, dt = None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), txt))


    def __init__(self):
        # Keep a reference to the "close" line in the data
        # x is BP y is RDSA
        self.dataclose_x = self.datas[0].close
        self.dataclose_y = self.datas[1].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None


    def notify_cashvalue(self, cash, value):
        self.log('Cash %s Value %s' % (cash, value))

    def notify_order(self, order):
        print(type(order), 'Is Buy ', order.isbuy())
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                        'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))


    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close(%s), %.2f' % (tickers[0], self.dataclose_x[0]))
        self.log('Close(%s), %.2f' % (tickers[1], self.dataclose_y[0]))

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            if (((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) <= (
                    2 * self.params.std * self.params.muti + self.params.avg)) and
                    ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) >= -(
                            2 * self.params.std * self.params.muti + self.params.avg))):
                # limit loss, we will not trade unless  -(2*std + 0.5) <= (BP-m*RSDA-b) <= (2*std + 0.5)

                # BUY
                # BP-m*RSDA-b >1*std + 0.5
                if ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) > (
                        self.params.std * self.params.muti + self.params.avg)):
                    self.log('SELL PORTFOLIO,SELL{},BUY{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell(self.datas[0], size = self.params.size)
                    self.order = self.buy(self.datas[1], size = int(self.params.m * self.params.size))

                # BP-m*RSDA-b <-(1*std + 0.5)
                elif ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) < -(
                        self.params.std * self.params.muti + self.params.avg)):
                    self.log('BUY PORTFOLIO,BUY{},SELL{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy(self.datas[0], size = self.params.size)
                    self.order = self.sell(self.datas[1], size = int(self.params.m * self.params.size))


        else:
            # this part is not exactly what I want but till now it is fine

            # if the price is too high we need to buy our portfolio back incase of risk(buy BP sell RDSA)
            if ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) >= (
                    2 * self.params.std * self.params.muti + self.params.avg)):
                self.log('CLOSE THE SELL LIMIT LOSS,BUY{},SELL{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(self.datas[0], size = self.params.size)
                self.order = self.sell(self.datas[1], size = int(self.params.m * self.params.size))

            # if the price is too low we need to sell our portfolio back incase of risk(sell BP buy RDSA)
            elif ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) <= -(
                    2 * self.params.std * self.params.muti + self.params.avg)):
                self.log('CLOSE THE BUY LIMIT LOSS,SELL{},BUY{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(self.datas[0], size = self.params.size)
                self.order = self.buy(self.datas[1], size = int(self.params.m * self.params.size))

            else:
                # SELL
                # -0.5 < BP-m*RSDA-b < 0.5            
                if (((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) < self.params.avg) and
                        ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) > -self.params.avg)):

                    # comes from higher portfolio value
                    if ((self.dataclose_x[0] - self.params.m * self.dataclose_y[0] - self.params.b) > 0):
                        self.log('CLOSE THE SELL,BUY{},SELL{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy(self.datas[0], size = self.params.size)
                        self.order = self.sell(self.datas[1], size = int(self.params.m * self.params.size))

                    # comes from lower portfolio value
                    else:
                        self.log('CLOSE THE BUY,SELL{},BUY{}'.format(self.dataclose_x[0], self.dataclose_y[0]))
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell(self.datas[0], size = self.params.size)
                        self.order = self.buy(self.datas[1], size = int(self.params.m * self.params.size))


# Run the model    
if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(PairStrategy)

    # load the data
    datalist = [
            ('data\\intra_' + tickers[0] + '_' + year + '_' + intra_freq + '.csv', variable_name[0]),  # [0] = Data file, [1] = Data name
            ('data\\intra_' + tickers[1] + '_' + year + '_' + intra_freq + '.csv', variable_name[1]),
    ]

    # Loop through the list adding to cerebro.
    for i in range(len(datalist)):
        data = bt.feeds.GenericCSVData(dataname = datalist[i][0],
                                       datetime = 0,
                                       open = 1,
                                       high = 2,
                                       low = 3,
                                       close = 4,
                                       openinterest = -1,
                                       time = -1,
                                       volume = -1,
                                       dtformat = "%Y-%m-%d %H:%M:%S",
                                       timeframe = bt.TimeFrame.Minutes,
                                       compression = 1)
        cerebro.adddata(data, name = datalist[i][1])

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake = 10)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission = 0.001)

    cerebro.addobserver(ValueObserver)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Print
    cerebro.plot(volume = False)
