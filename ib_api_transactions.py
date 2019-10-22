######################################################################################
# Description: Employing IB API to get contract information and then place order.    #
#              Place order through a prewritten json file.                           #
# Raw code form: https://gist.github.com/robcarver17/7b4a8e2f1fbfd70b4aaea5d205cb35eb#                                                            #
# Edited by: Ying Wang                                                               #
# Date: 4/09/18                                                                      #
######################################################################################

import datetime
import time
import logging
import logging.handlers
import json
import ib_api_trading
import ib_api_include
#import send_email
import traceback
import os
import ib_api_connect_config_wrapper
from pandas import DataFrame

###########
# M A I N #
###########

def setup_logger(my_logger_name, my_log_file, my_log_level=None, my_format=None, my_datefmt=None,
                my_filemode=None, my_maxBytes=None, my_fileRotatingCount=None):

    if my_format is None :
        my_format = '%(asctime)s %(message)s'
    if my_datefmt is None  :
        my_datefmt = '%m-%d %H:%M:%S'
    if my_filemode is None :
        my_filemode = 'a+w'
    if my_log_level is None :
        my_log_level = logging.INFO
    if my_maxBytes is None :
        my_maxBytes = 10000000; #rotate file if size reaches this
    if my_fileRotatingCount is None :
        my_fileRotatingCount = 4; #rotate file if size reaches this

    my_new_logger = logging.getLogger(my_logger_name)
    my_new_logger.setLevel(my_log_level)

    h = logging.handlers.RotatingFileHandler(my_log_file, mode=my_filemode,
            maxBytes=my_maxBytes, backupCount=my_fileRotatingCount, encoding=None, delay=False)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    my_new_logger.addHandler(h)

    return my_new_logger


if __name__ == '__main__':
    try: # Setup the log file and initilize the waiting list of future transactions.

        logger_server = setup_logger("logger_server_log",  "log_server.log",
                                     logging.INFO)
        logger_server.info("Check server")
        setup_logger("logger_report_log", "log_report.log", logging.WARNING)

        app = ib_api_connect_config_wrapper.TestApp(ib_api_include.ip, ib_api_include.port, ib_api_include.clientId)
        #logger_report = logging.getLogger('logger_report')

        enteredFileName = ib_api_include.enteredFileName
        generatedFileName = ib_api_include.generatedFileName
        app.logger_server.info("Log server info now is %s", datetime.datetime.now())
        app.logger_report.info("Log report info now is %s", datetime.datetime.now())
        waitingTransaction = [] # List with execution_time in the future.

    except:
        print(traceback.format_exc())
    try: # Entry point for the main transaction.
        while True:
            # First check the waiting list
            if not waitingTransaction:
                pass
            else:
                for transaction in waitingTransaction:
                    execution_time = datetime.datetime.strptime(transaction["execution_time"], '%Y-%m-%d %H:%M:%S')
                    # Execuate the transaction that with time  < current time.
                    if (execution_time < datetime.datetime.now()):
                        app.processContractAndOrder(transaction)
                        waitingTransaction.remove(transaction)
                    else:
                        pass

            # Generate the json file from the portfolio
            openExeFileOld = open(generatedFileName, 'r')
            tradingFileOld = json.load(openExeFileOld)
            openExeFileOld.close()

            # Update the json file
            ib_api_trading.IBTrading(app)

            # Check if there is differenc between the two files, if there is difference, then send email to the customer.
            openExeFileNew = open(generatedFileName, 'r')
            tradingFileNew = json.load(openExeFileNew)
            openExeFileNew.close()
            print(len(tradingFileOld['transactions']))
            if len(tradingFileOld['transactions']) == len(tradingFileNew['transactions']):
                executionFile = [generatedFileName, enteredFileName]
                print("1")
            else:
                #send_email.main(str(tradingFileNew))
                executionFile = [generatedFileName, enteredFileName]
                print("2")



            # Read the json file with transaction details.
            for file in executionFile:
                openExeFile = open(file, 'r')
                executionFile = json.load(openExeFile)
                openExeFile.close()
                # Convert time string to time format
                updated_time = datetime.datetime.strptime(executionFile["updated_time"], '%Y-%m-%d %H:%M:%S')
                previous_time = datetime.datetime.strptime(executionFile["previous_time"], '%Y-%m-%d %H:%M:%S')
                if (updated_time < previous_time):
                    pass
                elif (executionFile["ready_flag"] == False):
                    print(executionFile["ready_flag"])
                    pass
                else:
                    # Loop all the transactions in the json file, and filter with the type of contract

                    if executionFile["transactions"] != None:
                        for transaction in executionFile["transactions"]:
                            execution_time = datetime.datetime.strptime(transaction["execution_time"], '%Y-%m-%d %H:%M:%S')
                            if (execution_time < datetime.datetime.now()):
                                print(transaction)

                                app.processContractAndOrder(transaction)
                            else:
                                # Put the transaction with future execuation time in a waiting list.
                                waitingTransaction.append(transaction)
                                print(transaction["secType"] + "_" + transaction["symbol"] + " has been added to the waiting list!")
                                logger_report.warning(transaction["secType"] + "_" + transaction["symbol"] + " has been added to the waiting list!")

                # Update the json file with processed information.
                executionFile["ready_flag"] = False
                executionFile["previous_time"] = str(datetime.datetime.now())[0:-7]
                writeExeFile = open(file, 'w+')
                writeExeFile.write(json.dumps(executionFile, indent = 4))
                writeExeFile.close()
            print("Sleep 3 mins and then wake up for next run")
            time.sleep(ib_api_include.sleeptime)


            if datetime.datetime.now() >= datetime.datetime.strptime(str(datetime.datetime.now().date())   + ' 15:55:00', '%Y-%m-%d %H:%M:%S'):
                app.disconnect()
                print('Go to off market sleep')
                time.sleep(ib_api_include.offmarket_sleeptime)
                print('Program wait up')
                app = ib_api_connect_config_wrapper.TestApp(ib_api_include.ip, ib_api_include.port,
                                                            ib_api_include.clientId)


    except KeyboardInterrupt:
        print("Keyboard interrupted!")

