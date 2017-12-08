from botlog import BotLog


class BotTrade(object):
    def __init__(self, current_price, stop_loss=0):
        self.output = BotLog()
        self.status = "OPEN"
        self.entryPrice = current_price
        self.exitPrice = None
        self.output.log("Trade opened")
        if stop_loss:
            self.stop_loss = current_price - stop_loss

    def close(self, current_price):
        self.status = "CLOSED"
        self.exitPrice = current_price
        self.output.log("Trade closed")

    def tick(self, current_price):
        if self.stop_loss:
            if current_price < self.stop_loss:
                self.close(current_price)

    def show_trade(self):
        trade_status = "Entry Price: " + str(self.entryPrice) + " Status: " + str(self.status) + " Exit Price: " + str(
            self.exitPrice)

        if self.status == "CLOSED":
            trade_status = trade_status + " Profit: "
            if self.exitPrice > self.entryPrice:
                trade_status = trade_status + "\033[92m"
            else:
                trade_status = trade_status + "\033[91m"
            price_change = self.exitPrice - self.entryPrice
            trade_status = trade_status + str(price_change) + "\033[0m"

        self.output.log(trade_status)
