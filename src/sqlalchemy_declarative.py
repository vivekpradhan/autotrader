import sqlalchemy as sa
from base import Base
from secrets import *

#this is needed for ViewMyOrders Autoload.
engine = sa.create_engine(sql_address)


class ViewMyOrders(Base):
    __table__ = sa.Table('myOrders', Base.metadata,
        sa.Column('view_id', sa.String(36), primary_key=True),
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('cost', sa.Float, nullable=False),
        sa.Column('paid_currency', sa.String(10), nullable=False),
        sa.Column('fee', sa.Float, nullable=False),
        sa.Column('transaction_time', sa.DateTime, nullable=False),
        sa.Column('transaction_id', sa.String(50), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('order_type', sa.String(20), nullable=False),
            autoload=True, autoload_with=engine
        )

class CoinbaseOrders(Base):
    __tablename__ = 'myOrdersCoinbase'

    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Float, nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    paid_currency = sa.Column(sa.String(10), nullable=False)
    fee = sa.Column(sa.Float, nullable=False)
    transaction_time = sa.Column(sa.DateTime, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    platform = sa.Column(sa.String(20), nullable=False)
    order_type = sa.Column(sa.String(20), nullable=False)


class GDAXOrders(Base):
    __tablename__ = 'myOrdersGdax'

    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Float, nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    paid_currency = sa.Column(sa.String(10), nullable=False)
    fee = sa.Column(sa.Float, nullable=False)
    transaction_time = sa.Column(sa.DateTime, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    platform = sa.Column(sa.String(20), nullable=False)
    order_type = sa.Column(sa.String(20), nullable=False)


class BitfinexOrders(Base):
    __tablename__ = 'myOrdersBitfinex'

    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Float, nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    paid_currency = sa.Column(sa.String(10), nullable=False)
    fee = sa.Column(sa.Float, nullable=False)
    transaction_time = sa.Column(sa.DateTime, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    platform = sa.Column(sa.String(20), nullable=False)
    order_type = sa.Column(sa.String(20), nullable=False)

class GDAXOrderBook(Base):
    __tablename__ = 'orderBookGDAX'

    id = sa.Column(sa.BigInteger, primary_key=True)
    sequence_id = sa.Column(sa.BigInteger, nullable = False)
    entry_type = sa.Column(sa.String(10), nullable = False)
    order_type = sa.Column(sa.String(10), nullable = False)
    side = sa.Column(sa.String(10), nullable = False)
    coin = sa.Column(sa.String(10), nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)

class GDAXRawOrders(Base):
    __tablename__ = 'rawOrdersGDAX'

    id = sa.Column(sa.BigInteger, primary_key=True)
    sequence_id = sa.Column(sa.BigInteger, nullable = False)
    trade_id = sa.Column(sa.BigInteger, nullable = False)
    order_type_or_reason = sa.Column(sa.String(10), nullable = False)
    coin = sa.Column(sa.String(10), nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    client_oid = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)

class GDAXRawOrdersNew(Base):
    __tablename__ = 'rawOrdersGDAXNew'

    id = sa.Column(sa.BigInteger, primary_key=True)
    sequence_id = sa.Column(sa.BigInteger, nullable = False)
    trade_id = sa.Column(sa.BigInteger, nullable = False)
    entry_type = sa.Column(sa.String(10), nullable = False)
    order_type_or_reason = sa.Column(sa.String(10), nullable = False)
    side = sa.Column(sa.String(10), nullable = False)
    coin = sa.Column(sa.String(10), nullable=False)
    currency = sa.Column(sa.String(10), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    client_oid = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)

class DataErrors(Base):
    __tablename__ = 'dataErrors'
    id = sa.Column(sa.Integer, primary_key=True)
    logger = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    argv = sa.Column(sa.String(200), nullable=False)
    errortext = sa.Column(sa.Text,nullable=False)
    
class GADXHistoricalDataOneSecondOHLC(Base):
    __tablename__ = 'oneSecOHLCGdax'
    id = sa.Column(sa.Integer, primary_key=True)
    coin = sa.Column(sa.String(10), nullable=False)
    currency = sa.Column(sa.String(10), nullable=False) 
    timestamp = sa.Column(sa.DateTime,nullable=False)
    low = sa.Column(sa.Float,nullable=False)
    high = sa.Column(sa.Float,nullable=False)
    open = sa.Column(sa.Float,nullable=False)
    close = sa.Column(sa.Float,nullable=False)
    volume = sa.Column(sa.Float,nullable=False)

class historicalDataProgramState(Base):
    __tablename__='historicalDataProgramState'
    id = sa.Column(sa.Integer, primary_key=True)
    entry_type = sa.Column(sa.String(10), nullable=False)
    transaction_id = sa.Column(sa.String(50), nullable=False)
    start = sa.Column(sa.DateTime,nullable=False)
    end = sa.Column(sa.DateTime,nullable=False)
    platform = sa.Column(sa.String(10), nullable=False)
    status = sa.Column(sa.String(10), nullable=False)