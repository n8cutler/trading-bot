from poloniex import Poloniex
import urllib
import json
from botcandlestick import BotCandlestick


class BotChart(object):
    def __init__(self, exchange, pair, period, back_test=True):
        self.pair = pair
        self.period = period

        self.startTime = 1491048000
        self.endTime = 1491591200

        self.data = []

        if exchange == "poloniex":
            self.conn = Poloniex('key goes here', 'Secret goes here')

            if back_test:
                poloniex_data = self.conn.api_query("returnChartData",
                                                    {"currencyPair": self.pair,
                                                     "start": self.startTime,
                                                     "end": self.endTime,
                                                     "period": self.period,
                                                     })
                for datum in poloniex_data:
                    if datum['open'] and datum['close'] and datum['high'] and datum['low']:
                        self.data.append(BotCandlestick(self.period, datum['open'], datum['close'], datum['high'],
                                                        datum['low'], datum['weightedAverage']))

        if exchange == "bittrex":
            if back_test:
                url = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=" + self.pair + \
                      "&tickInterval=" + self.period + "&_=" + str(self.startTime)
                response = urllib.urlopen(url)
                raw_data = json.loads(response.read())
                self.data = raw_data["result"]

    def get_points(self):
        return self.data

    def get_current_price(self):
        current_values = self.conn.api_query("returnTicker")
        return current_values[self.pair]["last"]
