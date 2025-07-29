import ccxt

from ccxtools.base.CcxtExchange import CcxtExchange


class Bithumb(CcxtExchange):
    def __init__(self, who, env_vars):
        super().__init__(env_vars)
        self.ccxt_inst = ccxt.bithumb({
            'apiKey': env_vars(f'BITHUMB_API_KEY{who}'),
            'secret': env_vars(f'BITHUMB_SECRET_KEY{who}')
        })

    def get_last_price(self, ticker):
        res = self.ccxt_inst.fetch_ticker(f'{ticker}/KRW')
        return res['last']

    def get_last_prices(self, tickers):
        ticker_datas = self.ccxt_inst.fetch_tickers([f'{ticker}/KRW' for ticker in tickers])
        return {ticker: ticker_datas[f'{ticker}/KRW']['last'] for ticker in tickers}

    def get_best_book_price(self, ticker, side):
        order_book = self.ccxt_inst.fetch_order_book(f'{ticker}/KRW')[f'{side}s']
        return order_book[0][0]

    def post_market_order(self, ticker, side, amount, price):
        symbol = f'{ticker}/KRW'
        
        res = self.ccxt_inst.create_order(symbol, 'market', side, amount, price)
        order_data = self.ccxt_inst.fetch_order(res['id'], symbol)
        return order_data['average']
