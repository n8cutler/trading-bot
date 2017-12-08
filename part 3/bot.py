import argparse
import time
import urllib2

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick

REFRESH_SEC = 10
PERIODS = [300, 900, 1800, 7200, 14400, 86400]
CURRENCY_PAIRS = ["BTC_XMR", "BTC_USDT"]


class Bot:
    def __init__(self):
        self.options = self.get_options()

    @staticmethod
    def get_options():
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('-p', '--period', metavar='period', type=int, choices=PERIODS, default=PERIODS[0],
                            help='The moving average period in seconds to use')
        parser.add_argument('-c', '--currency_pair', metavar='currency_pair', choices=CURRENCY_PAIRS,
                            default=CURRENCY_PAIRS[0], help='The currency pair to use')
        parser.add_argument('-n', '--num_points', metavar='num_points', type=int, help='The number of points to use')
        parser.add_argument('-s', '--start_time', metavar='start_time', help='The time to start from')
        parser.add_argument('-e', '--end_time', metavar='end_time', help='The time to end at')

        return parser.parse_args()

    def run(self):
        if self.options.start_time:
            chart = BotChart("poloniex", self.options.currency_pair, self.options.period)

            strategy = BotStrategy()

            for candlestick in chart.get_points():
                strategy.tick(candlestick)

        else:
            chart = BotChart("poloniex", self.options.currency_pair, self.options.period, back_test=False)

            strategy = BotStrategy()

            candlesticks = []
            developing_candlestick = BotCandlestick()

            while True:
                try:
                    developing_candlestick.tick(chart.get_current_price())
                except urllib2.URLError:
                    time.sleep(REFRESH_SEC)
                    developing_candlestick.tick(chart.get_current_price())

                if developing_candlestick.is_closed():
                    candlesticks.append(developing_candlestick)
                    strategy.tick(developing_candlestick)
                    developing_candlestick = BotCandlestick()

                time.sleep(REFRESH_SEC)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
