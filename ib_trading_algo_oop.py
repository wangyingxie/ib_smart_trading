import pandas as pd
import datetime
class Stock_Algo:
    def __init__(self, profile_stock_threshold, item, tradingFile):
        self.quantity_sell = 0
        self.quantity_buy = 0
        self.stock_buying_threshold = profile_stock_threshold['stock_buying_threshold'][0]
        self.stock_shortterm_selling_threshold = profile_stock_threshold['stock_shortterm_selling_threshold'][0]
        self.item = item
        self.tradingFile = tradingFile

    def operateStock(self, tradingFile, action):
        self.tradingFile = tradingFile
        self.action = action
        transactions = {}
        transactions['order'] = []
        transactions['symbol'] = self.item['symbol']
        transactions['secType'] = self.item['secType']
        transactions['currency'] = self.item['currency']
        transactions['exchange'] = 'SMART'
        order_sell = {}
        order_sell['action'] = self.action
        order_sell['orderType'] = 'LMT'
        order_sell['totalQuantity'] = round(int(abs(self.quantity_sell)))
        order_sell['transmit'] = True
        order_sell["lmtPrice"] = int(self.item['marketPrice'])
        order_sell["tif"] = "DAY"
        transactions['order'].append(order_sell)
        transactions['execution_time'] = str(datetime.datetime.now())[0:-7]
        self.tradingFile['transactions'].append(transactions)
        return self.tradingFile

    def tradingStock(self):
        if self.item['marketPrice'] <= self.item['averageCost'] * (
                1 - self.stock_buying_threshold / 100):
            #  Buy this stock, subtract from the quantity
            self.quantity_buy = self.item['position']
            self.tradingFile = self.operateStock(self.tradingFile, 'BUY')
        elif self.item['marketPrice'] >= self.item['averageCost'] * (
                1 + self.stock_shortterm_selling_threshold / 100):
            # Sell this stock, add to the quantity
            self.quantity_sell = self.item['position']
            self.tradingFile = self.operateStock(self.tradingFile, 'SELL')
        return self.tradingFile

class Option_Algo:
    def __init__(self, option_profit_threshold, optPrice, undPrice, gamma, delta, theta, avgCost, multiplier, item, tradingFile, commissionFee):
        self.optPrice = optPrice
        self.undPrice = undPrice
        self.gamma = gamma
        self.delta = delta
        self.theta = theta
        self.avgCost = avgCost
        self.multiplier = multiplier
        self.item = item
        self.tradingFile = tradingFile
        self.commissionFee = commissionFee
        self.gammaThreshold = option_profit_threshold["gamma_threshold"].values[0]
        self.deltaThreshold = option_profit_threshold["gamma_threshold"].values[0]
        self.thetaThreshold = option_profit_threshold["gamma_threshold"].values[0]
        self.timeToExpire = option_profit_threshold["time_to_expire"].values[0]
        self.alpha_ITM_check_percentage = option_profit_threshold["alpha_ITM_check_percentage"].values[0]
        self.profit_taken_percentage = option_profit_threshold["profit_taken_percentage"].values[0]

    def optionBuyCallITMCheck(self):
        # Check if in the money for Call option
        if float(self.undPrice) >= float(self.avgCost)/ float(self.multiplier) + float(
            self.alpha_ITM_check_percentage) * float(self.avgCost) / float(
            self.multiplier) + float(self.item['strike']):
            return True

    def optionBuyPutITMCheck(self):
        # Check if in the money for Put option
        """
        if float(self.undPrice) + float(self.avgCost) / float(self.multiplier) + float(
                self.alpha_ITM_check_percentage) * float(self.avgCost) / float(
            self.multiplier) < float(self.item['strike']):
        """
        if float(self.undPrice) < float(self.item['strike']):
            return True

    def optionSellCallITMCheck(self):
        # Check if in the money for Call option
        if float(self.undPrice) >= float(self.avgCost) / float(self.multiplier) + float(self.item['strike']):
            return True

    def optionSellPutITMCheck(self):
        # Check if in the money for Put option
        if float(self.undPrice) + float(self.avgCost) / float(self.multiplier)/ float(
            self.multiplier) < float(self.item['strike']):
            return True

    def gammaDeltaCheck(self):

        # This is still potential to increase
        if abs(self.gamma) <= self.gammaThreshold and abs(self.delta) >= self.deltaThreshold:
            return True

    def remainValueCheck(self):
        # Sell the option, if the left value is larger than the commission fee.
        if float(self.optPrice) * float(self.multiplier) > self.commissionFee:
            return True

    def optionProfitCheck(self):
        # Close the option contract by selling them and check if the remain value is larger than the commission fee.
        if float(self.optPrice) >= self.avgCost * (1 + float(self.profit_taken_percentage)) / float(self.multiplier):
            return True

    def expireDateCheck(self):
        # Check the option expiration date
        # Check if the option will be expire in 4 days.

        if pd.to_datetime(self.item['lastTradeDateOrContractMonth'], format='%Y%m%d',
                          errors='ignore') - datetime.datetime.now() <= datetime.timedelta(int(self.timeToExpire)):
            return True

    def thetaTimeValueCheck(self):
        if abs(self.theta)/float(self.optPrice) >= self.thetaThreshold:
            return True

    def AssignOption(self):
        transactions = {}
        transactions['optionExercise'] = 'Yes'
        transactions['symbol'] = self.item['symbol']
        transactions['secType'] = self.item['secType']
        transactions['currency'] = self.item['currency']
        transactions['exchange'] = 'SMART'
        transactions['right'] = self.item['right']
        transactions["lastTradeDateOrContractMonth"] = str(self.item['lastTradeDateOrContractMonth'])
        transactions["strike"] = round(self.item['strike'],1)
        transactions["multiplier"] = str(self.item['multiplier'])
        transactions['execution_time'] = str(datetime.datetime.now())[0:-7]
        transactions['position'] = self.item['position']
        self.tradingFile['transactions'].append(transactions)
        return self.tradingFile

    def SellOption(self):
        transactions = {}
        transactions['order'] = []
        transactions['optionExercise'] = 'No'
        transactions['symbol'] = self.item['symbol']
        transactions['secType'] = self.item['secType']
        transactions['currency'] = self.item['currency']
        transactions['exchange'] = 'SMART'
        transactions['right'] = self.item['right']
        transactions["lastTradeDateOrContractMonth"] = str(self.item['lastTradeDateOrContractMonth'])
        transactions["strike"] = round(self.item['strike'],1)
        transactions["multiplier"] = str(self.item['multiplier'])
        order_buy = {}
        order_buy['action'] = 'SELL'
        order_buy['orderType'] = 'LMT'
        order_buy['totalQuantity'] = int(abs(self.item['position']))
        order_buy['transmit'] = True
        order_buy["lmtPrice"] = round(self.optPrice, 2)
        order_buy["tif"] = "DAY"
        transactions['order'].append(order_buy)
        transactions['execution_time'] = str(datetime.datetime.now())[0:-7]
        self.tradingFile['transactions'].append(transactions)
        return self.tradingFile

    def BuyOption(self):
        transactions = {}
        transactions['order'] = []
        transactions['symbol'] = self.item['symbol']
        transactions['secType'] = self.item['secType']
        transactions['currency'] = self.item['currency']
        transactions['exchange'] = 'SMART'
        transactions['right'] = self.item['right']
        transactions["lastTradeDateOrContractMonth"] = str(self.item['lastTradeDateOrContractMonth'])
        transactions["strike"] = round(self.item['strike'],1)
        transactions["multiplier"] = str(self.item['multiplier'])
        order_buy = {}
        order_buy['action'] = 'BUY'
        order_buy['orderType'] = 'LMT'
        order_buy['totalQuantity'] = int(abs(self.item['position']))
        order_buy['transmit'] = True
        order_buy["lmtPrice"] = round(self.optPrice, 2)
        order_buy["tif"] = "DAY"
        transactions['order'].append(order_buy)
        # transactions["currentPrice"] = int(item['marketPrice'])
        # transactions["tradingPriceDateTimeQuant_list"] = tradingPriceDateTimeQuant_list
        transactions['execution_time'] = str(datetime.datetime.now())[0:-7]
        self.tradingFile['transactions'].append(transactions)
        return self.tradingFile

    def optionBuyPutAlgo(self):
        # Trading a BUY PUT
        if self.expireDateCheck():
            # Check if in the money
            if self.optionBuyPutITMCheck():
                # Assign the option contract
                self.tradingFile = self.AssignOption()
            else:
                # Sell the option, if the left value is larger than the commission fee.
                if self.remainValueCheck():
                    self.tradingFile = self.SellOption()
        else:
            if self.optionBuyPutITMCheck():
                if self.gammaDeltaCheck():
                    # This is still potential to increase
                    pass
                else:
                    # Assign the option
                    self.tradingFile = self.AssignOption()
            else:
                if self.optionProfitCheck():
                    self.tradingFile = self.SellOption()

                else:
                    if self.gammaDeltaCheck():
                        pass
                    else:
                        #Check the remaining time value of the option
                        if self.thetaTimeValueCheck():
                            self.tradingFile = self.SellOption()
                        else:
                            pass


        return self.tradingFile

    def optionBuyCallAlgo(self):
        # Trading a BUY CALL
        # Check the option expiration date
        # Check if the option will be expire in 4 days.

        if self.expireDateCheck():
            if self.optionBuyCallITMCheck():
                # Assign the option contract
                self.tradingFile = self.AssignOption()
            else:
                # Sell the option, if the left value is larger than the commission fee.
                if self.remainValueCheck():
                    self.tradingFile = self.SellOption()
        else:
            if self.optionBuyCallITMCheck():
                if self.gammaDeltaCheck():
                    # This is still potential to increase
                    pass
                else:
                    # Assign the option
                    self.AssignOption()
            else:
                if self.optionProfitCheck():
                    self.tradingFile = self.SellOption()

                else:
                    if self.gammaDeltaCheck():
                        # This is still potential to increase
                        pass
                    else:
                        # Check the remaining time value of the option
                        if self.thetaTimeValueCheck():
                            self.tradingFile = self.SellOption()
                        else:
                            pass

        return self.tradingFile

    def optionSellPutAlgo(self):

        # Trading a SELL PUT
        # Check the option expiration date
        if self.expireDateCheck():

            if self.optionSellPutITMCheck():
                # Close the option contract by buying it back
                self.tradingFile = self.BuyOption()
            else:
                # Wait to take the premium
                pass
        else:
            # TTE is more than threshold
            if self.optionSellPutITMCheck():
                if self.gammaDeltaCheck():
                    # Close the option by buying the contract back.
                    self.tradingFile = self.BuyOption()
                else:
                    # May have positive luck if we wait
                    pass
            else:
                # Not ITM, wait to take the full premium
                pass
        return self.tradingFile

    def optionSellCallAlgo(self):
        # Trading a SELL CALL
        # Check the option expiration date
        if self.expireDateCheck():
            if self.optionSellCallITMCheck():
                # Close the option contract by buying it back
                self.tradingFile = self.BuyOption()
            else:
                # Wait to take the premium
                pass
        else:
            # TTE is more than threshold
            if self.optionSellCallITMCheck():
                if self.gammaDeltaCheck():
                    # Close the option by buying the contract back.
                    self.tradingFile = self.BuyOption()
                else:
                    # May have positive luck if we wait
                    pass
            else:
                # Not ITM, wait to take the full premium
                pass
        return self.tradingFile