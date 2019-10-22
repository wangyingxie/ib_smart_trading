import json
import requests
from xml.etree import ElementTree
import json
import pandas as pd
from pandas import DataFrame
import sys
from io import StringIO

def getOpenPosition(query_id = '317942'):
    ib_token = '297023187497428394385561'
    requestUrl = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t="+ib_token+"&q="+query_id+"&v=3"
    request_refcode = requests.get(requestUrl)
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

if __name__ == "__main__":
    openPosition = getOpenPosition()
    print(openPosition)



