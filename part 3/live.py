import time
import urllib2

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick


def main():
    chart = BotChart("poloniex", "BTC_XMR", 300, False)

    strategy = BotStrategy()

    candlesticks = []
    developing_candlestick = BotCandlestick()

    while True:
        try:
            developing_candlestick.tick(chart.get_current_price())
        except urllib2.URLError:
            time.sleep(int(30))
            developing_candlestick.tick(chart.get_current_price())

        if developing_candlestick.is_closed():
            candlesticks.append(developing_candlestick)
            strategy.tick(developing_candlestick)
            developing_candlestick = BotCandlestick()

        time.sleep(int(30))


if __name__ == "__main__":
    main()
