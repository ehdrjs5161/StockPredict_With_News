from pandas_datareader import data
import pandas as pd
import os
from pykrx import stock
import datetime
from server.pythonCode import method


def stock_price(code, begin):
    code = method.set_code(code)
    code = code+'.KS'
    frame = data.get_data_yahoo(code, begin)

    return frame

def market_info (code, begin):
    today = datetime.datetime.today().strftime("%Y%m%d")
    market = pd.DataFrame()
    code = method.set_code(code)
    marekt = stock.get_market_fundamental_by_date()
    print(code)
    if os.path.isfile("../market_info/" + code + ".csv"):
        market = pd.read_csv("./market_info/" + code + ".csv", encoding="UTF-8")
        last_day = datetime.datetime.strptime(market.iloc[-1]['날짜'], "%Y-%m-%d")
        last_day = datetime.datetime.strftime(last_day, "%Y%m%d")
        temp = stock.get_market_fundamental_by_date(last_day, today, code)
        market = pd.concat([market, temp])
    else:
        date = begin.replace("-", "")
        temp = stock.get_market_fundamental_by_date(date, today, code)
        market = pd.concat([market, temp])
    return market


if __name__ =="__main__":
    kospi200 = pd.read_csv("../file/KOSPI200.csv", encoding="UTF-8")[['code', 'name']]
    for code in kospi200['code']:
        temp = stock_price(code, "2012-01-01")
        temp.to_csv("../file/price/"+method.set_code(code)+".csv")