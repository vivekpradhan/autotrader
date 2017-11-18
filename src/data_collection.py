from sqlalchemy_declarative import CoinbaseOrders, GDAXOrders, BitfinexOrders, GDAXOrderBook, GDAXRawOrders
from secrets import *
from coinbase.wallet.client import Client
import gdax
import pandas as pd
import dateutil.parser
import numpy as np
import datetime
import urllib, json
from utils import *
import time




def bitfinex_orders():
    temp = pd.read_csv('../../notebooks/bitfinex-2017-11-05-trades.csv',dtype = {'#':str})
    df = pd.DataFrame()
    df['amount'] = temp['Amount'].abs()
    df['currency'] = temp['Pair'].apply(strip_pair_0)
    df['paid_currency'] = temp['Pair'].apply(strip_pair_1)
    df['cost'] = temp['Price']
    df['transaction_time'] = temp['Date'].apply(dateutil.parser.parse)
    df['transaction_id'] = temp['#']
    #print df['transaction_id'].dtype
    df['platform'] = 'bitfinex'
    df['fee'] = temp['Fee']
    df['type'] = np.where(temp['Amount']<0, 'sell', 'buy')
    pushNew2DB_bf(df,'BitfinexOrders')
                
def gdax_orders():
    auth_client = gdax.AuthenticatedClient(gdax_key, gdax_secret, gdax_passphrase)
    tradesx = []
    for item in auth_client.get_fills():
        trades = item
        trades = [[float(x['size']),x['product_id'].split('-')[0],float(x['price']), x['product_id'].split('-')[1], dateutil.parser.parse(x['created_at']), x['order_id'], 'gdax', float(x['fee']), x['side']] for x in trades] 
        tradesx += trades
    df=pd.DataFrame(tradesx,columns=['amount','currency','cost','paid_currency','transaction_time','transaction_id','platform','fee','type'])
    df['transaction_time'] = df['transaction_time'].apply(lambda d: pd.to_datetime(str(d)))
    prev_tid = ''
    gen_num = 1
    for idx,row in df.iterrows():
        temp = row['transaction_id']
        if row['transaction_id'] == prev_tid:
            df.set_value(idx,'transaction_id',row['transaction_id'] + '-' + str(gen_num).zfill(5))
            gen_num += 1
        else:
            gen_num = 1
        prev_tid = temp
    #print df[df['transaction_id'].duplicated(keep = False)]
    #print df
    pushNew2DB_gd(df,'GDAXOrders')
    

def coinbase_orders():
    client = Client(coinbase_apikey, coinbase_apisecret)
    response = client.get_accounts()['data']
    account_ids =  [x for x in [y['id'] for y in response]]
    t_list = []
    for account_id in account_ids:
        t_list+=[x for x in client.get_transactions(account_id)['data']]
    lst = [[abs(float(x['amount']['amount'])),x['amount']['currency'],float(x['native_amount']['amount'])/abs(float(x['amount']['amount'])),x['native_amount']['currency'],dateutil.parser.parse(x['created_at']),x['id'], 'coinbase',x['type']] for x in t_list if (x['type'] == 'buy' or x['type'] == 'sell' or x['type'] == 'fiat_deposit' or x['type'] == 'fiat_withdrawal')]
    df=pd.DataFrame(lst,columns=['amount','currency','cost','paid_currency','transaction_time','transaction_id','platform','type'])
    df['transaction_time'] = df['transaction_time'].apply(lambda d: pd.to_datetime(str(d)))
    df['fee'] = 0.0 
    df.loc[df.type == 'fiat_deposit', 'type'] = "DEPOSIT"
    df.loc[df.type == 'fiat_withdrawal', 'type'] = "WITHDRAWAL"
    df.loc[df.type == 'buy', 'type'] = "DEPOSIT"
    df.loc[df.type == 'sell', 'type'] = "WITHDRAWAL"
    pushNew2DB_cb(df,'CoinbaseOrders')

def get_hist_price(currency, datetimex):
    url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms=USD&ts={}'.format(currency,date2timestamp(datetimex))
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    if currency in data:
        if 'USD' in data[currency]:
            return data[currency]['USD']

#at the end of this call the current orderbook should be commited to db
#currencies = ["LTC-USD","LTC-BTC","ETH-USD","ETH-BTC","BTC-USD"]
def get_gdax_orderbook(currencies):
    public_client =  gdax.PublicClient()
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    updates = []
    t0 = time.time()
    for pair in currencies:
        timex = datetime.datetime.utcnow()
        a = public_client.get_product_order_book(pair,level=3)
        if 'sequence' in a:
            sequence_id = int(a['sequence'])
        else:
            errorlogger('gdaxOrderbook', 'sequence not in reply', pair, 'key not found')
            sequence_id = -999
        if 'bids' in a:
            for entry in a['bids']:
                updates.append(make_dict(float(entry[0]),float(entry[1]), entry[2], sequence_id, 'bid', pair, timex))
        else:
            errorlogger('gdaxOrderbook', 'bids not in reply', pair, 'key not found')
        if 'asks' in a:
            for entry in a['asks']:
                updates.append(make_dict(float(entry[0]),float(entry[1]), entry[2], sequence_id, 'ask', pair, timex))
        else:
            errorlogger('gdaxOrderbook', 'asks not in reply', pair, 'key not found')
    engine.execute(
        GDAXOrderBook.__table__.insert(),
        updates
    )

class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["LTC-USD","LTC-BTC","ETH-USD","ETH-BTC","BTC-USD"]
        self.batch_updates = []
        self.batch_timer = time.time()
    def commit_batch(self):
        try:
            if len(self.batch_updates) > 0:
                engine = sa.create_engine(sql_address)
                engine.execute(
                GDAXRawOrders.__table__.insert(),
                self.batch_updates
                )
        except Exception,e:
            print self.batch_updates
            errorlogger('rawGdaxOrders', 'Failed Update', 'nothing', str(e))
        self.batch_updates = []
    def on_message(self, msg):
        try:
            update = createUpdateFromRaw(msg)
        except Exception,e:
            errorlogger('rawGdaxOrders', 'Failed dictgen', 'nothing', str(e))
        self.batch_updates.append(update)
        if time.time() - self.batch_timer >= 1.0:
            self.commit_batch()
            self.batch_timer = time.time()
    def on_close(self):
        self.commit_batch()