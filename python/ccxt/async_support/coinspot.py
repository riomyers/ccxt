# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import NotSupported


class coinspot (Exchange):

    def describe(self):
        return self.deep_extend(super(coinspot, self).describe(), {
            'id': 'coinspot',
            'name': 'CoinSpot',
            'countries': ['AU'],  # Australia
            'rateLimit': 1000,
            'has': {
                'CORS': False,
                'createMarketOrder': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28208429-3cacdf9a-6896-11e7-854e-4c79a772a30f.jpg',
                'api': {
                    'public': 'https://www.coinspot.com.au/pubapi',
                    'private': 'https://www.coinspot.com.au/api',
                },
                'www': 'https://www.coinspot.com.au',
                'doc': 'https://www.coinspot.com.au/api',
                'referral': 'https://www.coinspot.com.au/join/FSM11C',
            },
            'api': {
                'public': {
                    'get': [
                        'latest',
                    ],
                },
                'private': {
                    'post': [
                        'orders',
                        'orders/history',
                        'my/coin/deposit',
                        'my/coin/send',
                        'quote/buy',
                        'quote/sell',
                        'my/balances',
                        'my/orders',
                        'my/buy',
                        'my/sell',
                        'my/buy/cancel',
                        'my/sell/cancel',
                    ],
                },
            },
            'markets': {
                'BTC/AUD': {'id': 'btc', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD', 'baseId': 'btc', 'quoteId': 'aud'},
                'LTC/AUD': {'id': 'ltc', 'symbol': 'LTC/AUD', 'base': 'LTC', 'quote': 'AUD', 'baseId': 'ltc', 'quoteId': 'aud'},
                'DOGE/AUD': {'id': 'doge', 'symbol': 'DOGE/AUD', 'base': 'DOGE', 'quote': 'AUD', 'baseId': 'doge', 'quoteId': 'aud'},
            },
            'commonCurrencies': {
                'DRK': 'DASH',
            },
        })

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostMyBalances(params)
        result = {'info': response}
        if 'balance' in response:
            balances = response['balance']
            currencyIds = list(balances.keys())
            for i in range(0, len(currencyIds)):
                currencyId = currencyIds[i]
                uppercase = currencyId.upper()
                code = self.common_currency_code(uppercase)
                account = {
                    'free': balances[currencyId],
                    'used': 0.0,
                    'total': balances[currencyId],
                }
                result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'cointype': market['id'],
        }
        orderbook = await self.privatePostOrders(self.extend(request, params))
        return self.parse_order_book(orderbook, None, 'buyorders', 'sellorders', 'rate', 'amount')

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        response = await self.publicGetLatest(params)
        id = self.market_id(symbol)
        id = id.lower()
        ticker = response['prices'][id]
        timestamp = self.milliseconds()
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        request = {
            'cointype': self.market_id(symbol),
        }
        return await self.privatePostOrdersHistory(self.extend(request, params))

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        method = 'privatePostMy' + self.capitalize(side)
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        request = {
            'cointype': self.market_id(symbol),
            'amount': amount,
            'rate': price,
        }
        return await getattr(self, method)(self.extend(request, params))

    async def cancel_order(self, id, symbol=None, params={}):
        raise NotSupported(self.id + ' cancelOrder() is not fully implemented yet')
        # method = 'privatePostMyBuy'
        # return await getattr(self, method)({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests')
        url = self.urls['api'][api] + '/' + path
        if api == 'private':
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.json(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/json',
                'key': self.apiKey,
                'sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
