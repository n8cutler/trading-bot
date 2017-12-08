from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade


class BotStrategy(object):
    def __init__(self):
        self.output = BotLog()
        self.prices = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.current_price = ""
        self.current_close = ""
        self.num_concurrent_trades = 1
        self.indicators = BotIndicators()

    def tick(self, candlestick):
        self.current_price = float(candlestick.price_average)
        self.prices.append(self.current_price)

        # self.current_close = float(candlestick['close'])
        # self.closes.append(self.current_close)

        self.output.log("Price: " + str(candlestick.price_average) + "\tMoving Average: " +
                        str(self.indicators.moving_average(self.prices, 15)))

        self.evaluate_positions()
        self.update_open_trades()
        self.show_positions()

    def evaluate_positions(self):
        open_trades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                open_trades.append(trade)

        if len(open_trades) < self.num_concurrent_trades:
            if self.current_price < self.indicators.moving_average(self.prices, 15):
                self.trades.append(BotTrade(self.current_price, stop_loss=.0001))

        for trade in open_trades:
            if self.current_price > self.indicators.moving_average(self.prices, 15):
                trade.close(self.current_price)

    def update_open_trades(self):
        for trade in self.trades:
            if trade.status == "OPEN":
                trade.tick(self.current_price)

    def show_positions(self):
        for trade in self.trades:
            trade.show_trade()
