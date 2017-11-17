from sqlalchemy_declarative import CoinbaseOrders, GDAXOrders, BitfinexOrders, ViewMyOrders,DataErrors
from secrets import *
from base import Base
import sqlalchemy as sa
import pandas as pd
import datetime





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