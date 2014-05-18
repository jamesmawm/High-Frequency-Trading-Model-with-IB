#######################################
# Author: James Ma
# Email stuff here: jamesmawm@gmail.com
#######################################

#!/usr/bin/env python
# -*- noplot -*-

"""

This example shows how to use matplotlib to provide a data cursor.  It
uses matplotlib to draw the cursor and may be a slow since this
requires redrawing the figure with every mouse move.

Faster cursoring is possible using native GUI drawing, as in
wxcursor_demo.py
"""
#from __future__ import print_function
from pylab import *
import matplotlib.ticker as ticker

ax, ax2 = None, None
colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
graphs = []
graphs2 = []


class Cursor:
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text( 0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes: return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y )
        self.ly.set_xdata(x )

        self.txt.set_text( 'x=%1.2f, y=%1.2f'%(x,y) )
        draw()


class SnaptoCursor:
    def __init__(self, ax, x, y):
        self.ax = ax
        #self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='r')  # the vert line
        self.x = x
        self.y = y

        self.txt = ax.text( 0.7, 0.9, '', transform=ax.transAxes) # text location in axes coords

    def set_x_labels(self, xlabels):
        self.xlabels = xlabels

    def mouse_move(self, event):

        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata

        indx = int(x) #searchsorted(self.x, [x])[0]
        if indx >= len(self.xlabels):
            indx = len(self.xlabels)-1

        #y = self.y[indx]
        xstr = self.xlabels[indx]

        # update the line positions
        #self.lx.set_ydata(y)
        self.ly.set_xdata(x)
        self.txt.set_text( 'x=%s, y=%1.4f'%(xstr, y) )
        draw()


def setup_plots(x, ys, ys2):
    global ax, ax2, graphs2, graphs

    fig = plt.figure()
    #ax = fig.add_subplot(211)
    ax = fig.add_subplot(111)

    # TODO: interactive charts do not seem to work with live updates.
    cursor = SnaptoCursor(ax, x, ys[0])     #cursor = Cursor(ax)
    #cursor.set_x_labels(xlabels)

    plt.title("Prices and Standard Deviations")
    graphs = []
    for i, y_series in enumerate(ys):
        color = colors[i % len(colors)]
        graph = ax.plot(range(0, len(x)), y_series, color=color, lw=1)[0]
        graphs.append(graph)
    ax.grid()
    connect('motion_notify_event', cursor.mouse_move)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.3f'))

    # TODO: use subplot when standard deviation graph is ready.
    #ax2 = fig.add_subplot(212, sharex=ax)
    #graphs2 = []
    #current_length = len(xlabels)
    #for i, std_series in enumerate(ys2):
    #    y_series = get_subplot_yseries(std_series, current_length)
    #    graph = plot_subplot(i, y_series) #ax2.plot(range(0, len(y_series)), y_series, color=color, lw=1)[0]
    #    graphs2.append(graph)
    #ax2.grid(True)
    #ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.3f'))

    ion()
    show()


def get_subplot_yseries(std_series, current_length):
    length = len(std_series)
    if length < current_length:
        y_series = np.zeros(current_length-length-1)
        y_series = np.hstack((y_series, std_series))
        return y_series
    return std_series


def plot_subplot(i, y_series):
    color = colors[i % len(colors)]
    graph = ax2.plot(range(0, len(y_series)), y_series, color=color, lw=1)[0]
    return graph


def update_subplot(ys2, current_length, x_series):
    global ax2, graphs2

    for i, std_series in enumerate(ys2):
        y_series = get_subplot_yseries(std_series, current_length)
        if len(graphs2) == 0:
            graph = plot_subplot(i, y_series)
            graphs2.append(graph)
        else:
            graph = graphs2[i]
            graph.set_ydata(y_series)
            x_series = range(0, len(y_series))
            graph.set_xdata(x_series)
            ax2.relim()
            ax2.autoscale_view(True,True,True)
        draw()


def update_plot(ys, ys2, bid, ask):
    global ax, graphs

    ion()
    last_price = 0

    length = len(ys[0])
    x_series = None
    for i, y_series in enumerate(ys):
        x_series = range(0, length)
        graph = graphs[i]
        graph.set_ydata(y_series)
        graph.set_xdata(x_series)
        ax.relim()
        ax.autoscale_view(True,True,True)
        draw()

        if i==0:
            last_price = y_series[-1]

    plot_title = "bid:", bid, " ask:", ask, " last:", round(last_price, 3)
    plt.title(plot_title)

    # TODO: Turn on subplot when standard deviation graph is ready.
    #current_length = len(x_series)
    #update_subplot(ys2, current_length, x_series)