import sys

from botchart import BotChart
from botstrategy import BotStrategy


def main(argv):
    if argv:
        print "arguments: {}".format(argv)
    chart = BotChart("poloniex", "BTC_XMR", 300)
    strategy = BotStrategy()

    for candlestick in chart.get_points():
        strategy.tick(candlestick)


if __name__ == "__main__":
    main(sys.argv[1:])
