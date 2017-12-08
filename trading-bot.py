import datetime
import getopt
import sys
import time
from poloniex import Poloniex


def main(argv):
    period = 10
    pair = "BTC_XMR"
    prices = []
    current_moving_avg = 0
    moving_avg_len = 0
    start_time = False
    end_time = False
    historical_data = False
    trade_placed = False
    type_of_trade = False
    data_date = ""
    order_number = ""

    try:
        opts, args = getopt.getopt(argv, "hp:c:n:s:e:", ["period=", "currency=", "points="])
    except getopt.GetoptError:
        print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
            sys.exit()
        elif opt in ("-p", "--period"):
            if int(arg) in [300, 900, 1800, 7200, 14400, 86400]:
                period = arg
            else:
                print 'Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments'
                sys.exit(2)
        elif opt in ("-c", "--currency"):
            pair = arg
        elif opt in ("-n", "--points"):
            moving_avg_len = int(arg)
        elif opt in "-s":
            start_time = arg
        elif opt in "-e":
            end_time = arg

    conn = Poloniex('key goes here', 'key goes here')

    if start_time:
        historical_data = conn.api_query("returnChartData", {"currencyPair": pair, "start": start_time, "end": end_time,
                                                             "period": period})
    while True:
        if start_time and historical_data:
            next_data_point = historical_data.pop(0)
            last_pair_price = next_data_point['weightedAverage']
            data_date = datetime.datetime.fromtimestamp(int(next_data_point['date'])).strftime('%Y-%m-%d %H:%M:%S')
        elif start_time and not historical_data:
            exit()
        else:
            current_values = conn.api_query("returnTicker")
            last_pair_price = current_values[pair]["last"]
            data_date = datetime.datetime.now()

        if len(prices) > 0:
            current_moving_avg = sum(prices) / float(len(prices))
            previous_price = prices[-1]
            if not trade_placed:
                if (last_pair_price > current_moving_avg) and (last_pair_price < previous_price):
                    print "SELL ORDER"
                    order_number = conn.sell(pair, last_pair_price, .01)
                    trade_placed = True
                    type_of_trade = "short"
                elif (last_pair_price < current_moving_avg) and (last_pair_price > previous_price):
                    print "BUY ORDER"
                    order_number = conn.buy(pair, last_pair_price, .01)
                    trade_placed = True
                    type_of_trade = "long"
            elif type_of_trade == "short":
                if last_pair_price < current_moving_avg:
                    print "EXIT TRADE"
                    conn.cancel(pair, order_number)
                    trade_placed = False
                    type_of_trade = False
            elif type_of_trade == "long":
                if last_pair_price > current_moving_avg:
                    print "EXIT TRADE"
                    conn.cancel(pair, order_number)
                    trade_placed = False
                    type_of_trade = False

        print "%s Period: %ss %s: %s Moving Average: %s" % (data_date, period, pair, last_pair_price,
                                                            current_moving_avg)

        prices.append(float(last_pair_price))
        prices = prices[-moving_avg_len:]
        if not start_time:
            time.sleep(int(period))


if __name__ == "__main__":
    main(sys.argv[1:])
