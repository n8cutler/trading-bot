import hmac
import hashlib
import json
import time
import urllib
import urllib2


def create_time_stamp(date_str, str_format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(date_str, str_format))


class Poloniex:
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    @staticmethod
    def post_process(before):
        after = before

        # Add timestamps if there isn't one but is a datetime
        if 'return' in after:
            if isinstance(after['return'], list):
                for x in xrange(0, len(after['return'])):
                    if isinstance(after['return'][x], dict):
                        if 'datetime' in after['return'][x] and 'timestamp' not in after['return'][x]:
                            after['return'][x]['timestamp'] = float(create_time_stamp(after['return'][x]['datetime']))
        return after

    def api_query(self, command, req=None):

        if command == "returnTicker" or command == "return24Volume":
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif command == "returnOrderBook":
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' +
                                                  str(req['currencyPair'])))
            return json.loads(ret.read())
        elif command == "returnMarketTradeHistory":
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" +
                                                  '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif command == "returnChartData":
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=returnChartData&currencyPair=' +
                                                  str(req['currencyPair']) + '&start=' + str(req['start']) + '&end=' +
                                                  str(req['end']) + '&period=' + str(req['period'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.api_key
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            json_ret = json.loads(ret.read())
            return self.post_process(json_ret)

    def return_ticker(self):
        return self.api_query("returnTicker")

    def return_24h_volume(self):
        return self.api_query("return24Volume")

    def return_order_book(self, currency_pair):
        return self.api_query("returnOrderBook", {'currencyPair': currency_pair})

    def return_market_trade_history(self, currency_pair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currency_pair})

    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def return_balances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def return_open_orders(self, currency_pair):
        return self.api_query('returnOpenOrders', {"currencyPair": currency_pair})

    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def return_trade_history(self, currency_pair):
        return self.api_query('returnTradeHistory', {"currencyPair": currency_pair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The currency pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self, currency_pair, rate, amount):
        return self.api_query('buy', {"currencyPair": currency_pair, "rate": rate, "amount": amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The currency pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self, currency_pair, rate, amount):
        return self.api_query('sell', {"currencyPair": currency_pair, "rate": rate, "amount": amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The currency pair
    # orderNumber   The order number to cancel
    # Outputs:
    # success        1 or 0
    def cancel(self, currency_pair, order_number):
        return self.api_query('cancelOrder', {"currencyPair": currency_pair, "orderNumber": order_number})

    # Immediately places a withdrawal for a given currency, with no email confirmation.
    # In order to use this method, the withdrawal privilege must be enabled for your API key.
    # Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})
