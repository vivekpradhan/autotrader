import sys
from data_collection import coinbase_orders,gdax_orders
from utils import errorlogger
import time

config = sys.argv[1]
cmd = config.split('_')[0]
if cmd == 'GDAXraw':
    print 'gdaxraw'
elif cmd == 'GDAXorderbook':
    splitx = config.split('_')
    time_delta = int(splitx[1])
    while(1):
        try:
            get_gdax_orderbook()
            time.sleep(time_delta*60)
        except Exception,e:
            errorlogger('getGDAXOrderBook', 'Failed Update', config, str(e))
elif cmd == 'updateMyOrders':
    splitx = config.split('_')
    time_delta = int(splitx[1])
    if len(splitx) == 3:
        dontLoop = True
    else:
        dontLoop = False
    while(1):
        try:
            coinbase_orders()
            gdax_orders()
            if dontLoop:
                break
            time.sleep(time_delta*60)
        except Exception,e:
            errorlogger('updateMyOrders', 'Failed Update', config, str(e))
