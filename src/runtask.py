import sys
from data_collection import coinbase_orders,gdax_orders,myWebsocketClient,get_gdax_orderbook
from utils import errorlogger
import time

config = sys.argv[1]
cmd = config.split('_')[0]
#run with GDAXraw
if cmd == 'GDAXraw':
    wsClient = myWebsocketClient()
    print wsClient.error
    wsClient.start()
    print 'started'
    while not wsClient.error:
        time.sleep(5)
        print 'all good'
    errorlogger('GDAXraw', 'Failed', config, str(wsClient.error))
    print wsClient.error
    wsClient.close()
#call with GDAXorderbook_[time-in-mins]_LTC-USD#LTC-BTC#ETH-USD#ETH-BTC#BTC-USD
elif cmd == 'GDAXorderbook':
    splitx = config.split('_')
    time_delta = int(splitx[1])
    currencylist = splitx[2]
    currencies = [x for x in currencylist.split('#')]
    while(1):
        try:
            get_gdax_orderbook(currencies)
            time.sleep(time_delta*60)
        except Exception,e:
            errorlogger('getGDAXOrderBook', 'Failed Update', config, str(e))
#call with updateMyOrders_[time-in-mins] or updateMyOrders
elif cmd == 'updateMyOrders':
    splitx = config.split('_')
    if len(splitx) == 2:
        dontLoop = False
        time_delta = int(splitx[1])
    else:
        dontLoop = True
        time_delta = 0
    while(1):
        try:
            coinbase_orders()
            gdax_orders()
            if dontLoop:
                break
            time.sleep(time_delta*60)
        except Exception,e:
            errorlogger('updateMyOrders', 'Failed Update', config, str(e))
else:
	print "unrecognized CMD"
