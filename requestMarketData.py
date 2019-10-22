######################################################################################
# Description: Employing IB API to get contract information and then place order.    #
#              Place order through a prewritten json file.                           #
# Raw code form: https://gist.github.com/robcarver17/7b4a8e2f1fbfd70b4aaea5d205cb35eb#                                                            #
# Edited by: Ying Wang                                                               #
# Date: 4/09/18                                                                      #
######################################################################################

import datetime
import queue
from copy import deepcopy
from threading import Thread

from ibapi.client import EClient
from ibapi.contract import Contract as IBcontract
from ibapi.execution import ExecutionFilter
from ibapi.order import Order
from ibapi.wrapper import EWrapper
import os
import time
import logging
import json
from pprint import pprint
from pandas import DataFrame, Series

import datetime
from dateutil.relativedelta import relativedelta
import ib_api_include
## these are just arbitrary numbers in leiu of a policy on this sort of thing
from ibapi.contract import Contract as IBcontract
from ibapi.utils import iswrapper
import json
import requests
from xml.etree import ElementTree
import json
import pandas as pd
import sys
from io import StringIO

def getOpenPosition(query_id = '317942'):
    ib_token = '297023187497428394385561'
    requestUrl = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t="+ib_token+"&q="+query_id+"&v=3"
    request_refcode = requests.get(requestUrl)
    time.sleep(5)
    xml = str(request_refcode.content)
    tags = xml.split('<')
    referenceCode = tags[4][-10:]
    getUrl = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement?q="+referenceCode+"&t="+ib_token+"&v=3"
    result = requests.get(getUrl).text
    result = StringIO(result)
    openPosition = pd.read_csv(result, sep=",")
    return openPosition

def optionTobeExercised(query_id = '318306'):
    ib_token = '297023187497428394385561'
    requestUrl = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t="+ib_token+"&q="+query_id+"&v=3"
    request_refcode = requests.get(requestUrl)
    xml = str(request_refcode.content)
    tags = xml.split('<')
    referenceCode = tags[4][-10:]
    getUrl = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement?q="+referenceCode+"&t="+ib_token+"&v=3"
    result = requests.get(getUrl).text
    result = StringIO(result)
    optionTobeExercised = pd.read_csv(result, sep=",")
    return optionTobeExercised

class TestWrapper(EWrapper):

    def __init__(self):
        EWrapper.__init__(self)

    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        print("Account list:", accountsList)

    '''
    def updateAccountValue(self, key: str, val: str, currency: str,accountName: str):
        super().updateAccountValue(key, val, currency, accountName)
        print("UpdateAccountValue. Key:", key, "Value:", val,"Currency:", currency, "AccountName:", accountName)
    '''

    def updatePortfolio(self, contract: str, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                                accountName)
        print("UpdatePortfolio.", contract.symbol, "", contract.secType, "@", contract.exchange, "Position:", position,
              "MarketPrice:", marketPrice, "MarketValue:", marketValue, "AverageCost:", averageCost, "UnrealizedPNL:",
              unrealizedPNL, "RealizedPNL:", realizedPNL, "AccountName:", accountName)
        portfolio.append(
            [contract.symbol, contract.secType, contract.exchange, position, marketPrice, marketValue, averageCost,
             unrealizedPNL, realizedPNL, accountName])
    # ! [tickprice]

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        #print("Tick Price. Ticker Id:", reqId, "tickType:", tickType,
              #"Price:", price, "CanAutoExecute:", attrib.canAutoExecute,
              #"PastLimit:", attrib.pastLimit, end=' ')
        marketdataPrice.append([reqId, tickType, price, attrib.canAutoExecute])
    # ! [tickprice]


    # ! [ticksize]
    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)
        #print("Tick Size. Ticker Id:", reqId, "tickType:", tickType, "Size:", size)
        marketdataSize.append([reqId, tickType, size])

    # ! [ticksize]

    # ! [tickgeneric]
    def tickGeneric(self, reqId, tickType, value):
        super().tickGeneric(reqId, tickType, value)
        #print("Tick Generic. Ticker Id:", reqId, "tickType:", tickType, "Value:", value)
    # ! [tickgeneric]

    # ! [tickstring]
    def tickString(self, reqId, tickType, value):
        super().tickString(reqId, tickType, value)
        #print("Tick string. Ticker Id:", reqId, "Type:", tickType, "Value:", value)
    # ! [tickstring]

    # ! [ticksnapshotend]
    def tickSnapshotEnd(self, reqId):
        super().tickSnapshotEnd(reqId)
        #print("TickSnapshotEnd:", reqId)
    # ! [ticksnapshotend]

    def newsProviders(self, newsProviders):
        print("newsProviders:")
        for provider in newsProviders:
            print(provider)
    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str, headline: str, extraData: str):
        print("tickNews: ", tickerId, ", timeStamp: ", timeStamp,", providerCode: ", providerCode, ", articleId: ", articleId,", headline: ", headline, "extraData: ", extraData)

    '''
    def updateAccountTime(self, timeStamp: str):
        super().updateAccountTime(timeStamp)
        print("UpdateAccountTime. Time:", timeStamp)

    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)

        print("Account download finished:", accountName)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        print("Acct Summary. ReqId:", reqId, "Acct:", account,"Tag: ", tag, "Value:", value, "Currency:", currency)

    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        print("AccountSummaryEnd. Req Id: ", reqId)
'''

class TestClient(EClient):
    def __init__(self, wrapper):
        ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

class TestApp(TestWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)
        global portfolio
        portfolio = []
        global marketdataPrice
        marketdataPrice = []
        global marketdataSize
        marketdataSize = []
        self.connect(ipaddress, portid, clientid)
        thread = Thread(target=self.run)
        thread.start()
        self.reqManagedAccts()
        self.reqAccountUpdates(True, ib_api_include.accountID)
        self.reqAccountSummary(9003, "All", "$LEDGER:EUR")
        self.reqNewsProviders()
    def reqMktData(self, reqId, ibcontract):
        super().reqMktData(reqId, ibcontract, "", False, False, [])
    def reqMktNews(self, reqId, ibcontract):
        super().reqMktData(reqId + 1, ibcontract, "mdoff,292:BRFG", False, False, [])
        super().reqMktData(reqId + 2, ibcontract, "mdoff,292:BRFUPDN", False, False, [])
        super().reqMktData(reqId + 3, ibcontract, "mdoff,292:DJNL", False, False, [])


def SetupLogger():
    if not os.path.exists(ib_api_include.executionDirectory + "/log"):
        os.makedirs(ib_api_include.executionDirectory + "/log")
    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    timefmt = '%y%m%d_%H:%M:%S'
    logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)


###########
# M A I N #
###########


def main():
    SetupLogger()
    logging.info("now is %s", datetime.datetime.now())
    openPosition = getOpenPosition()
    print(openPosition)
    app = TestApp(ib_api_include.ip, ib_api_include.port, ib_api_include.clientId)
    time.sleep(ib_api_include.sleeptime_trading)
    summary = DataFrame(portfolio, columns = ['symbol', 'secType', 'exchange', 'position', 'marketPrice', 'marketValue', 'averageCost', 'unrealizedPNL', 'realizedPNL', 'accountName'])
    reqId = 1000
    #watchlist_stock_treshold = pd.read_excel('my_ib_threshold.xlsx', sheet_name = 'watchlist_stock_treshold')
    #watchlist_stock_treshold = DataFrame(watchlist_stock_treshold)
    for i in range(0, len(openPosition)):
        record = openPosition.iloc[i]
        ibcontract = IBcontract()
        ibcontract.secType = record.AssetClass
        ibcontract.symbol = record.UnderlyingSymbol
        ibcontract.exchange = "SMART"
        ibcontract.currency = record.CurrencyPrimary
        ibcontract.lastTradeDateOrContractMonth = record.Expiry
        ibcontract.strike = record.Strike
        ibcontract.multiplier = record.Multiplier
        ibcontract.right = record["Put/Call"]
        app.reqMktData(reqId, ibcontract)

        ibcontract = IBcontract()
        ibcontract.symbol = "MU"
        ibcontract.exchange = "SMART"
        ibcontract.secType = "STK"
        app.reqMktNews(reqId, ibcontract)
        time.sleep(30)
        print(DataFrame(marketdataPrice, columns=["reqId", "tickType", "tickPrice", "CanAutoExecuteOrNot"]))
        print(DataFrame(marketdataSize, columns=["reqId", "tickType", "tickSize"]))
        reqId += 1

    app.disconnect()

if __name__ == '__main__':
    main()