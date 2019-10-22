######################################################################################
# Description: Employing IB API to get contract information and then place order.    #
#              Place order by generating a json file using threshold and algorithms. #                                                           #
# Edited by: Ying Wang                                                               #
# Date: 4/09/18                                                                      #
######################################################################################


import time
import logging
from pandas import DataFrame, Series
import datetime
import ib_api_include
import json
import pandas as pd
import ib_trading_algo_oop
import ib_api_connect_config_wrapper
#import global_settings
import numpy as np
##############
# IB Trading #
##############
#app.logger_report = logging.getLogger('app.logger_report')
#app.logger_server = logging.getLogger('app.logger_server')

def IBTrading(app):
    #SetupLogger() Already setup in the main script

    app.logger_report.warning("Algorithm checktime: %s", datetime.datetime.now())
    time.sleep(ib_api_include.sleeptime_trading)

    # Get the open position for the account. Through flex query delayed data
    #openPosition = GetOpenPosition()

    reqId = 1
    # Reteieve the market data and news for the open options.

    # Get the open position from the portfolio
    portfolio = app.reqPortfolio()
    portfSummary = DataFrame(portfolio, columns = ['symbol', 'secType', 'exchange', 'currency','lastTradeDateOrContractMonth', 'multiplier', 'right', 'strike', 'position', 'marketPrice', 'marketValue', 'averageCost', 'unrealizedPNL', 'realizedPNL', 'accountName' ])
    portfSummary = portfSummary.drop_duplicates(subset = ['symbol', 'secType', 'exchange', 'currency','lastTradeDateOrContractMonth', 'multiplier', 'right', 'strike'], keep = 'first')
    print(portfSummary)

    reqArraySize = ib_api_include.reqArraySize
    reqIdList = list(range(1,reqArraySize*len(portfSummary)+1)) # Not hard coded, replace 4 with REQ_ARRAY_SIZE

    symList = []
    secTypeList = []
    app.logger_report.warning("Portfolio:{}".format(portfSummary))

    for i in range(0, len(portfSummary)):
        item = portfSummary.iloc[i]
        symList += [item['symbol']] * reqArraySize
        secTypeList += [item['secType']] *reqArraySize
    reqIdSymList = DataFrame({"reqId":reqIdList, "symbol": symList, 'secType': secTypeList})

    marketReturn = app.GetMarketDataNews(portfSummary, reqId, reqArraySize)
    # Sheet names, profile_stock_threshold, profile_opt_threshold, watchlist_stock_treshold, watchlist_opt_threshold
    profile_stock_threshold = pd.read_excel(ib_api_include.thresholdFileName, sheet_name = 'profile_stock_threshold')
    option_profit_threshold = pd.read_excel(ib_api_include.thresholdFileName, sheet_name = 'profile_opt_threshold')
    watchlist_stock_treshold = pd.read_excel(ib_api_include.thresholdFileName, sheet_name = 'watchlist_stock_treshold')
    watchlist_stock_treshold = DataFrame(watchlist_stock_treshold)
    tickTypeIdMapping = pd.read_csv(ib_api_include.tickTypeIdMapping, index_col = None)
    tickTypeIdMapping["TickId"] = tickTypeIdMapping["TickId"].astype(int)
    marketPrice = DataFrame(marketReturn[0], columns=["reqId", "tickTypeId", "price", "executeNow"])
    marketSize = DataFrame(marketReturn[1], columns=["reqId", "tickTypeId", "volume"])
    optionInfo = DataFrame(marketReturn[2], columns=["reqId", "tickTypeId", "optionInfo", "delta", "optPrice", "pvDividend", "gamma", "vega", "theta", "undPrice"])
    #Check if it is live trading
    if datetime.datetime.now() >= datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 15:55:00','%Y-%m-%d %H:%M:%S') \
            and datetime.datetime.now() < datetime.datetime.strptime(str(datetime.datetime.now().date()) + ' 09:30:00','%Y-%m-%d %H:%M:%S'):
        print("Trading not alive!")
        return None
    news = DataFrame(marketReturn[3], columns=["tickerId", "timeStamp", "providerCode", "articleId", "headline", "effect"])
    portfSummary = marketReturn[4]
    marketPrice = pd.merge(marketPrice, tickTypeIdMapping, left_on = "tickTypeId", right_on = "TickId", how = "left")
    marketSize = pd.merge(marketSize, tickTypeIdMapping, left_on= "tickTypeId", right_on="TickId", how="left")
    optionInfo = pd.merge(optionInfo, tickTypeIdMapping, left_on= "tickTypeId", right_on="TickId", how="left")
    print("Here is the portfolio")
    print(portfSummary)
    marketPrice = pd.merge(marketPrice, reqIdSymList, on = "reqId", how = "left")
    marketSize = pd.merge(marketSize, reqIdSymList, on = "reqId", how="left")
    optionInfo = pd.merge(optionInfo, reqIdSymList, on = "reqId", how="left")
    app.logger_report.warning("marketPrice:{}".format(marketPrice))
    app.logger_report.warning("marketSize:{}".format(marketSize))
    app.logger_report.warning("optionInfo:{}".format(optionInfo))
    news = pd.merge(news, reqIdSymList, left_on="tickerId", right_on = "reqId", how="left")

    # Use AI model to build up the model for the option or the stock.
    my_ib_trading = open(ib_api_include.generatedFileName, 'r')
    tradingFile = json.load(my_ib_trading)
    my_ib_trading.close()
    tradingFile["ready_flag"] = True
    tradingFile["previous_time"] = str(datetime.datetime.now() - datetime.timedelta(minutes = 1))[0:-7]
    tradingFile["updated_time"] = str(datetime.datetime.now())[0:-7]
    tradingFile['transactions'] = []
    print(portfSummary)
    commissionFee = ib_api_include.commissionFee

    for index, item in portfSummary.iterrows():
        if item['secType'] == 'STK':
            Stock_Algo = ib_trading_algo_oop.Stock_Algo(profile_stock_threshold, item, tradingFile)
            tradingFile = Stock_Algo.tradingStock()
    for index, item in portfSummary.iterrows():
        if item['secType'] == 'OPT':
            # Get the option information
            infoIndivOption = app.GetInfoIndivOption(optionInfo, item)
            print(infoIndivOption)
            if infoIndivOption != 'Yes':
                print(infoIndivOption)
                optPrice = infoIndivOption[0]
                undPrice = infoIndivOption[1]
                gamma = infoIndivOption[2]
                delta = infoIndivOption[3]
                theta = infoIndivOption[4]
                avgCost = infoIndivOption[5]
                multiplier = infoIndivOption[6]
                Option_Algo = ib_trading_algo_oop.Option_Algo(option_profit_threshold, optPrice, undPrice, gamma,
                                                                delta, theta, avgCost, multiplier, item, tradingFile,
                                                                commissionFee)

                # Merge the option in portfolio with the option price, size and the option Greek values.
                if item['position'] > 0 and item['right'] == 'P':
                    tradingFile = Option_Algo.optionBuyPutAlgo()
                elif item['position'] < 0 and item['right'] == 'P':
                    tradingFile = Option_Algo.optionSellPutAlgo()
                elif item['position'] > 0 and item['right'] == 'C':
                    tradingFile = Option_Algo.optionBuyCallAlgo()
                elif item['position'] < 0 and item['right'] == 'C':
                    tradingFile = Option_Algo.optionSellCallAlgo()

            elif infoIndivOption == 'Yes':
                pass

    app.logger_report.warning(tradingFile)
    writeExeFile = open(ib_api_include.generatedFileName, 'w+')
    writeExeFile.write(json.dumps(tradingFile, indent=4))
    writeExeFile.close()

"""
if __name__ == '__main__':
    app = ib_api_connect_config_wrapper.TestApp(ib_api_include.ip, ib_api_include.port, ib_api_include.clientId)
    IBTrading(app)
"""