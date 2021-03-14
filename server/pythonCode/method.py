import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict
import os
from server.pythonCode import getPrice, getNews, method, DB_Handler

mongo = DB_Handler.DBHandler()
db_name = "stockPredict"

def csv_to_json(data):
    return data.to_dict("records")

def set_code(code):
    code = str(code)
    if len(code) < 6:
        for j in range(0, 6 - len(code)):
            code = '0' + code
    return code

def search_code(company, frame):
    codes = []
    name = company
    code = frame['기업명'] == name
    code = list(frame['종목코드'][code])
    codes.append(code[0])
    code = set_code(str(codes[0]))

    return code

def code_to_name(frame, code):
    name = frame['종목코드'] == int(code)
    name = list(frame['기업명'][name])
    return name[0]

def load_data(company):
    code = set_code(company.code)
    news = mongo.find_item(condition={"code": "{}".format(code)}, db_name=db_name, collection_name="news")
    price = mongo.find_item(condition={"code": "{}".format(code)}, db_name=db_name, collection_name="price")

    if news is None:
        today = method.date_to_str(datetime.datetime.today())
        news = getNews.crawling(company.name, begin="2012-01-01", end=today)
        news_json = csv_to_json(news)
        news_input = OrderedDict()
        news_input['code'] = code
        news_input['news'] = news_json
        mongo.insert_item(data=news_input, db_name=db_name, collection_name="news")
        news = news
    else:
        news = pd.DataFrame(news['news'])

    if price is None:
        price = getPrice.stock_price(code, "2012-01-01")
        price.to_csv("price/"+code+'.csv', encoding="UTF-8")
        price = pd.read_csv("price/"+code+".csv")[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        price_json = csv_to_json(price)
        price_input = OrderedDict()
        price_input['code'] = code
        price_input['price'] = price_json
        mongo.insert_item(data=price_input, db_name=db_name, collection_name="price")
        price = price
    else:
        price = pd.DataFrame(price['price'])

    return news, price

def swift_type(news):
    days = []
    for i in range(0, len(news)):
        day = datetime.datetime.strptime(news[i], "%Y.%m.%d").strftime("%Y-%m-%d")
        days.append(day)
    news['date'] = days

    return news

def str_to_date(string):
    date = datetime.datetime.strptime(string, "%Y-%m-%d")
    return date

def date_to_str(date):
    date = date.strftime("%Y-%m-%d")
    return date

def day_range(begin, end):
    day_list = []
    begin = datetime.datetime.strptime(begin, "%m.%d")
    end = datetime.datetime.strptime(end, "%m.%d")

    date_gen = [begin +datetime.timedelta(days=x) for x in range(0, (end-begin).days)]
    for date in date_gen:
        day_list.append(date.strftime("%m.%d"))
    day_list.append(end.strftime("%m.%d"))
    return day_list

def news_union(code):
    news = pd.DataFrame()
    for i in range(1, 6):
        temp = pd.read_csv("./crawlingBatch/temporary_news/"+code+"_"+str(i)+".csv")[['Date', "Title"]]
        news = pd.concat([news, temp])

    return news

def merge(news, price, col1, col2):
    data = pd.merge(price, news, left_on="{}".format(col1), right_on="{}".format(col2))
    return data

def re_sizing(batch_size, data):
    batch = batch_size
    size = len(data)
    cnt = 0
    if size % batch != 0:
        while size % batch != 0:
            size = size - 1
            cnt += 1
    return cnt

def inverseTransform(Scaler, normed_data):
    real_data = []
    for i in range(0, len(normed_data)):
        temp = []
        for j in range(0, len(normed_data[0])):
            temp.append(Scaler.inverse_transform([[normed_data[i][j], 0, 0]])[0][0])
        real_data.append(temp)
    return real_data

def inverseTransform_day7(Scaler, normed_data):
    real_data = []
    for i in range(0, len(normed_data)):
        temp = []
        for j in range(0, len(normed_data[0])):
            temp.append(Scaler.inverse_transform([[normed_data[i][j], 0, 0]])[0][0])
        real_data.append(temp)

    return real_data

def rate(last_price, predict, day):
    if day == 1:
        rate = 100 * (predict - last_price[-1])/last_price[-1]
        return rate
    else:
        rate = []
        for i in range(0, len(predict)):
            if i == 0:
                rate.append(100 * (predict[i] - last_price[-1])/last_price[-1])
            else:
                rate.append(100 * (predict[i]-predict[i-1])/predict[i-1])
        return rate

def sent_result(frame):
    frame = np.array(frame)
    cnt = 1
    sum = frame[0][1]

    date = []
    label = []

    for j in range(len(frame) - 1):
        temp = frame[j + 1][1]
        if frame[j][0] == frame[j + 1][0]:
            cnt += 1
            sum += temp
        else:
            date.append(frame[j][0])
            label.append(sum / cnt)
            cnt = 1
            sum = frame[j][1]
        if j == len(frame) - 2:
            date.append(frame[j][0])
            label.append(sum / cnt)

    result = pd.DataFrame({'Date': date, 'Label': label})
    return result