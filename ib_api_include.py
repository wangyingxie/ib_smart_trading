# Define the variables used in the module

ip = "127.0.0.1"
port = 9004
clientId = 123
# Waiting for api to fetch data
sleeptime_trading = 15
# Time to wake up for next running
sleeptime = 180
# Initial trading file
enteredFileName = 'my_ib_transactions.json'
# Created trading file based on 'ib_api_trading.py'
generatedFileName = 'my_ib_trading.json'
# Threshold to buy or sell the stocks
thresholdFileName = 'my_ib_threshold.xlsx'
# Tick Type Id mapping
tickTypeIdMapping = 'tickTypeIdMapping.csv'
# The trading history
activityStatement = 'activity_statement_flex.csv'
# The log directory
log_dir = 'C:/Users/yiwang/PycharmProjects/misc/log/'
executionDirectory = 'C:/Users/yiwang/PycharmProjects/misc'

accountID = 'DU1018262'
#accountID = 'DU228246'

# Off market time
offmarket_sleeptime = 16*60*60

# The request array side for news
reqArraySize = 4

# The commission fee
commissionFee = 1
