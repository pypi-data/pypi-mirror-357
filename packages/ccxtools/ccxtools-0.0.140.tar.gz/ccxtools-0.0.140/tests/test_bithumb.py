import pytest

from src.ccxtools.bithumb import Bithumb


@pytest.fixture
def bithumb(env_vars):
    return Bithumb('', env_vars)


def test_get_last_price(bithumb):
    price = bithumb.get_last_price('BTC')
    assert isinstance(price, float)


def test_get_last_prices(bithumb):
    # Test input Start
    tickers = ['ETH', 'XRP']
    # Test input End

    prices = bithumb.get_last_prices(tickers)
    assert isinstance(prices, dict)
    for ticker in tickers:
        assert ticker in prices
        assert isinstance(prices[ticker], float)


def test_get_best_book_price(bithumb):
    assert isinstance(bithumb.get_best_book_price('BTC', 'ask'), float)
    assert isinstance(bithumb.get_best_book_price('BTC', 'bid'), float)


def test_post_market_order(bithumb):
    # Test input Start
    ticker = 'XRP'
    amount = 10
    # Test input End

    last_price = bithumb.get_last_price(ticker)
    
    buy_price = bithumb.post_market_order(ticker, 'buy', amount, last_price)
    assert 0.9 * last_price < buy_price < 1.1 * last_price
    
    sell_price = bithumb.post_market_order(ticker, 'sell', amount, last_price)
    assert 0.9 * last_price < sell_price < 1.1 * last_price
