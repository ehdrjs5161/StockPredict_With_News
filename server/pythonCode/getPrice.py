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
    kospi200 = pd.read_csv("../file/KOSPI200.csv", encoding="UTF-8")[['종목코드', '기업명']]
    for code, name in zip(kospi200['종목코드'], kospi200['기업명']):
        market = market_info(code, "20120101")
        market.to_csv("../market_info/"+method.set_code(code)+".csv", encoding="UTF-8")
        print(method.set_code(code)+"'s market_info completed")