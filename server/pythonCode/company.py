import pandas as pd
import datetime
from . import modeling, method, getNews, getPrice, DB_Handler
import os
from collections import OrderedDict

mongo = DB_Handler.DBHandler()
db_name = "stockPredict"

class companys:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.news =None
        self.price = None
        self.label = None
        self.newNews = None
        self.newPrice = None
        self.features = None
        self.model_day1 = None
        self.model_day7 = None
        self.result_day1 = None
        self.result_day7 = None
        self.update_day = None
        self.unit = None
        self.epoch = None

    def load_data(self):
        self.news, self.price = method.load_data(self)
        self.update_day = self.news['Date'].iloc[-1]
        print(self.update_day)

    def update_data(self):
        yesterday = method.date_to_str(datetime.datetime.today()-datetime.timedelta(days=1))
        last_news = self.news['Date'].iloc[-1]
        last_news = method.str_to_date(last_news)
        self.update_day = last_news

        yesterday = method.str_to_date(yesterday)
        # 가지고 있는 뉴스 데이터의 마지막 날짜와 어제 날짜를 비교하여 뉴스 데이터 중 어제 뉴스가 포함되지 않다면 크롤링해서 저장.
        if self.update_day < yesterday:
            print("Update News & Price")
            begin = self.update_day + datetime.timedelta(days=1)
            self.newNews = getNews.crawling(name=self.name, begin=method.date_to_str(begin), end=method.date_to_str(yesterday))
            newNews = method.csv_to_json(self.newNews)

            for news in newNews:
                mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$push': {'news': news}}, db_name=db_name, collection_name="news")
            self.news = pd.concat([self.news, self.newNews])

            temp = getPrice.stock_price(self.code, begin=self.update_day)
            temp.to_csv("file/price/"+self.code+".csv", encoding="UTF-8")
            self.newPrice = pd.read_csv("price/"+self.code+".csv", encoding="UTF-8")[['Date', 'High', 'Low', 'Open', 'Close', 'Volume']]
            newPrice = method.csv_to_json(self.newPrice)

            for price in newPrice:
                mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$push': {'price': price}}, db_name=db_name, collection_name="price")

            self.price = pd.concat([self.price, self.newPrice])

            print("Updating News & Price is completed!")
        else:
            print(self.name+"'s News & Price data are already Updated!")
        self.update_day = yesterday

    def model_setting(self, batch, term, features):
        self.features = features
        if features == 2:
            if not os.path.isfile("model/model_day1/" + self.code + "/saved_model.pb"):
                print("predict 1 day Model Compiling...")
                self.model_day1 = modeling.modeling(batch, term, self.features)
                self.model_day1 = modeling.model_educate(self, term, batch, 1)
            else:
                self.model_day1 = modeling.load_model(self.code, predict_day=1, features=features)
                print("predict 1 day Model load completed!")

            # if not os.path.isfile("model/model_day7/" + self.code + "/saved_model.pb"):
            #     print("predict 7 days Model Compiling...")
            #     self.model_day7 = modeling.modeling_day7(batch, term, self.features)
            #     self.model_day7 = modeling.model_educate(self, term, batch, 7)
            #     print("predict 7 days Model load completed!")
            # else:
            #     self.model_day7 = modeling.load_model(self.code, predict_day=7, features=features)
            #     print("predict 7 day Model load completed!")
        else:
            if not os.path.isfile("model/model_day1/withNews/" + self.code + "/saved_model.pb"):
                print("predict 1 day Model Compiling...")
                self.model_day1 = modeling.modeling(batch, term, self.features)
                self.model_day1 = modeling.model_educate(self, term, batch, 1)
            else:
                self.model_day1 = modeling.load_model(self.code, predict_day=1, features=features)
                print("predict 1 day Model load completed!")

            # if not os.path.isfile("model/model_day7/withNews/" + self.code + "/saved_model.pb"):
            #     print("predict 7 days Model Compiling...")
            #     self.model_day7 = modeling.modeling_day7(batch, term, self.features)
            #     self.model_day7 = modeling.model_educate(self, term, batch, 7)
            #     print("predict 7 days Model load completed!")
            #
            # else:
            #     print("Load model..")
            #     self.model_day7 = modeling.load_model(self.code, predict_day=7, features=features)

    def predict_price_day1(self):
        self.result_day1 = modeling.predict_day1(self)

    def predict_price_day7(self):
        self.result_day7 = modeling.predict_day7(self)

    def test_predict_day1(self):
        modeling.test_day1(self)

    def test_predict_day7(self):
        modeling.test_day7(self)

    def model_update(self):
        # 한번 모델링 해놓으면 당분간 안해도 됨.
        self.model_day1, self.model_day7 = modeling.update_model(self)
        print("Model Update Completed!")

    def result_save(self):
        company = OrderedDict()
        rate = OrderedDict()

        company["name"] = self.name
        company["code"] = self.code
        rate['code'] = self.code
        rate['name'] = self.name
        temp = []
        for i in range(0, len(self.result_day1['Time'])):
            price = {'Date': '{}'.format(self.result_day1['Time'][i]),
                     'Price': '{}'.format(int(self.result_day1['Price'][i]))}
            temp.append(price)
        company['price_day1'] = temp

        temp = []
        # for i in range(0, len(self.result_day7['Time'])):
        #     price = {'Date': '{}'.format(self.result_day7['Time'][i]),
        #              'Price': '{}'.format(int(self.result_day7['Price'][i]))}
        #     temp.append(price)
        # company['price_day7'] = temp

        company['predict_day1'] = int(self.result_day1['Predict'][0][0])

        # temp = []
        # for i in range(0, len(self.result_day7['Predict'][0])):
        #     predict = {'Date': '{}'.format(str(i + 1) + " day After"),
        #                'Price': '{}'.format(int(self.result_day7["Predict"][0][i]))}
        #     temp.append(predict)
        #
        # company['predict_day7'] = temp

        last_price1 = self.result_day1['Price'][-1]
        rate1 = 100 * (company['predict_day1'] - last_price1) / last_price1
        rate['predict_rate1'] = round(rate1, 2)

        temp = []
        for i in range(len(self.result_day7['Predict'][0])):
            if i == 0:
                rate2 = round(100 * (self.result_day7['Predict'][0][1] - self.result_day7['Price'][-1]) /
                              self.result_day7['Price'][-1], 2)
            else:
                rate2 = round(100 * (self.result_day7['Predict'][0][i] - self.result_day7['Predict'][0][i - 1]) /
                              self.result_day7['Predict'][0][i - 1], 2)
            temp.append(rate2)
        rate['predict_rate2'] = temp
        company['rate'] = rate

        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value=company, db_name=db_name, collection_name="predictResult")
        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value=rate, db_name=db_name, collection_name="rank")
