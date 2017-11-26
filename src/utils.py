from sqlalchemy_declarative import CoinbaseOrders, GDAXOrders, BitfinexOrders, GDAXOrderBook, GDAXRawOrders,GADXHistoricalDataOneSecondOHLC,historicalDataProgramState,DataErrors
from secrets import *
from base import Base
import sqlalchemy as sa
import pandas as pd
import datetime
import dateutil.parser
import uuid





def timestamp2date(timestamp):
    # function converts a Uniloc timestamp into Gregorian date
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

def date2timestamp(date):
    # function coverts Gregorian date in a given format to timestamp
    datex = datetime.datetime.strptime(date, '%Y-%m-%d')
    return int((time.mktime(datex.timetuple())+datex.microsecond/1e6))
def create_dbs():
    engine = sa.create_engine(sql_address)
    Base.metadata.create_all(engine)

def getStartAndEndHistoric():
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    update = session.query(historicalDataProgramState).filter(sa.and_(historicalDataProgramState.status == 'incomplete',historicalDataProgramState.entry_type == 'update')).first()
    if update:
        start = update.end + datetime.timedelta(seconds=1)
        order = session.query(historicalDataProgramState).filter(sa.and_(historicalDataProgramState.transaction_id == update.transaction_id,historicalDataProgramState.entry_type == 'order')).first()
        end = order.end
        return start,end,order.transaction_id
    order = session.query(historicalDataProgramState).filter(sa.and_(historicalDataProgramState.status == 'incomplete',historicalDataProgramState.entry_type == 'order')).first()
    if order:
        start = order.start
        end = order.end
        return start,end,order.transaction_id
    return None,None,None

def insertHistoricJob(start, end):
    tid = str(uuid.uuid4())
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    new_order = historicalDataProgramState(entry_type = 'order',transaction_id = tid,start=start,end=end,platform='GDAX',status='incomplete')
    session.add(new_order)
    session.commit()


def getEntryFromRow(row,classname):
    dbentry = globals()[classname]()
    dbentry.amount = row['amount']
    dbentry.currency = row['currency']
    dbentry.cost = row['cost']
    dbentry.paid_currency = row['paid_currency']
    dbentry.fee = row['fee']
    dbentry.transaction_time = row['transaction_time']
    dbentry.transaction_id = row['transaction_id']
    dbentry.platform = row['platform']
    dbentry.order_type = row['type']
    return dbentry

def pushNew2DB_cb(df,classname):
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    df.sort_values(by='transaction_time', ascending=True, inplace=True)
    timex = session.query(CoinbaseOrders).order_by(CoinbaseOrders.transaction_time.desc()).first()
    if timex == None:
        timex = datetime.datetime(1988, 1, 1)
    else:
        timex = timex.transaction_time
    
    for index, row in df.iterrows():
        if row['transaction_time']>timex:
            tid = session.query(CoinbaseOrders).filter(CoinbaseOrders.transaction_id == row['transaction_id']).first()
            if tid == None:
                new_entry = getEntryFromRow(row,classname)
                session.add(new_entry)
                session.commit()


def pushNew2DB_gd(df,classname):
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    df.sort_values(by='transaction_time', ascending=True, inplace=True)
    timex = session.query(GDAXOrders).order_by(GDAXOrders.transaction_time.desc()).first()
    if timex == None:
        timex = datetime.datetime(1988, 1, 1)
    else:
        timex = timex.transaction_time
    
    for index, row in df.iterrows():
        if row['transaction_time']>=timex:
            #print row['transaction_id']
            tid = session.query(GDAXOrders).filter(GDAXOrders.transaction_id == row['transaction_id']).first()
            if tid == None:
                #print 'yes'
                new_entry = getEntryFromRow(row,classname)
                session.add(new_entry)
                session.commit()
def pushNew2DB_bf(df,classname):
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    df.sort_values(by='transaction_time', ascending=True, inplace=True)
    timex = session.query(BitfinexOrders).order_by(BitfinexOrders.transaction_time.desc()).first()
    if timex == None:
        timex = datetime.datetime(1988, 1, 1)
    else:
        timex = timex.transaction_time
    
    for index, row in df.iterrows():
        if row['transaction_time']>timex:
            tid = session.query(BitfinexOrders).filter(BitfinexOrders.transaction_id == row['transaction_id']).first()
            if tid == None:
                new_entry = getEntryFromRow(row,classname)
                session.add(new_entry)
                session.commit()

def make_dict(costx, amountx, tid, seq_id, tpe, pair, timex):
    tmp = pair.split('-')
    coinx = tmp[0]
    currencyx = tmp[1]
    return dict(sequence_id = seq_id, order_type = tpe, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, timestamp = timex)



def strip_pair_0(x):
    return x.split('/')[0]
def strip_pair_1(x):
    return x.split('/')[1]

def errorlogger(loggerx, descriptionx, argvx, etext):
    engine = sa.create_engine(sql_address)
    Base.metadata.bind = engine
    DBSession = sa.orm.sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    new_error = DataErrors(logger = loggerx, description = descriptionx, timestamp = datetime.datetime.utcnow(), argv = argvx, errortext = etext)
    session.add(new_error)
    session.commit()

def createUpdateFromRaw(msg):
    if msg['type'] == 'received' and msg['order_type'] == 'limit':
        seq_id = msg['sequence']
        etype = msg['type']
        tpe = msg['order_type']
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        amountx = float(msg['size'])
        costx = float(msg['price'])
        tid = msg['order_id']
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'received' and msg['order_type'] == 'market':
        seq_id = msg['sequence']
        etype = msg['type']
        tpe = msg['order_type']
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        amountx = 0
        if 'funds' in msg:
            costx = float(msg['funds'])
        else:
            costx = 0
        tid = msg['order_id']
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'open':
        seq_id = msg['sequence']
        etype = msg['type']
        tpe = ''
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        amountx = float(msg['remaining_size'])
        costx = float(msg['price'])
        tid = msg['order_id']
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'done':
        seq_id = msg['sequence']
        etype = msg['type']
        tpe = msg['reason']
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        if 'remaining_size' in msg:
            amountx = float(msg['remaining_size'])
        else:
            amountx = 0.0
        if 'price' in msg:
            costx = float(msg['price'])
        else:
            costx = 0.0
        tid = msg['order_id']
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'match':
        seq_id = msg['sequence']
        trid = msg['trade_id']
        etype = msg['type']
        tpe = ''
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        amountx = float(msg['size'])
        costx = float(msg['price'])
        tid = msg['taker_order_id']
        coid = msg['maker_order_id']
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = trid , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'change':
        seq_id = msg['sequence']
        etype = msg['type']
        tpe = ''
        sidex = msg['side']
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        if 'new_size' in msg:
            amountx = float(msg['new_size'])
        elif 'new_funds' in msg:
            amountx = float(msg['new_funds'])
        try:
            costx = float(msg['price'])
        except:
            costx = 0
        tid = msg['order_id']
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = dateutil.parser.parse(msg['time'])
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    elif msg['type'] == 'activate':
        seq_id = 0
        etype = ''
        tpe = ''
        sidex = ''
        tmp = msg['product_id'].split('-')
        coinx = tmp[0]
        currencyx = tmp[1]
        amountx = 0.0
        costx = 0.0
        tid = ''
        if 'client_oid' in msg:
            coid = msg['client_oid']
        else:
            coid = ''
        timex = datetime.datetime.fromtimestamp(float(msg['timestamp']))
        update = dict(sequence_id = seq_id, trade_id = 0 , entry_type = etype, order_type_or_reason = tpe, side = sidex, coin = coinx, currency = currencyx, amount = amountx, cost = costx, transaction_id = tid, client_oid = coid, timestamp = timex)
    return update
