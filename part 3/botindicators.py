import numpy


class BotIndicators(object):
    def __init__(self):
        pass

    @staticmethod
    def moving_average(data_points, period):
        if len(data_points) > 1:
            return sum(data_points[-period:]) / float(len(data_points[-period:]))

    @staticmethod
    def momentum(data_points, period=14):
        if len(data_points) > period - 1:
            return data_points[-1] * 100 / data_points[-period]

    @staticmethod
    def ema(prices, period):
        x = numpy.asarray(prices)
        weights = numpy.exp(numpy.linspace(-1., 0., period))
        weights /= weights.sum()

        a = numpy.convolve(x, weights, mode='full')[:len(x)]
        a[:period] = a[period]
        return a

    def macd(self, prices, n_slow=26, n_fast=12):
        ema_slow = self.ema(prices, n_slow)
        ema_fast = self.ema(prices, n_fast)
        return ema_slow, ema_fast, ema_fast - ema_slow

    @staticmethod
    def rsi(prices, period=14):
        deltas = numpy.diff(prices)
        seed = deltas[:period + 1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down
        rsi = numpy.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                up_val = delta
                down_val = 0.
            else:
                up_val = 0.
                down_val = -delta

            up = (up * (period - 1) + up_val) / period
            down = (down * (period - 1) + down_val) / period
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

            if len(prices) > period:
                return rsi[-1]
            else:
                return 50  # output a neutral amount until enough prices in list to calculate RSI
