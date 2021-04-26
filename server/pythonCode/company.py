import pandas as pd
import datetime
from . import modeling, method, getNews, getPrice, DB_Handler ,naverAPI
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
        self.newNews = None
        self.newPrice = None
        self.features = None
        self.model_day1 = None
        self.result_day1 = None
        self.update_day = None

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
            print(len(self.newNews))
            if len(self.newNews) > 0:
                self.newNews = method.sent_result(self.newNews[['Date', 'Label']])
                newNews = method.csv_to_json(self.newNews)
                for news in newNews:
                    mongo.update_item(condition={"code": "{}".format(self.code)},
                                      update_value={'$push': {'news': news}}, db_name=db_name, collection_name="news")
                self.news = pd.concat([self.news, self.newNews])
            # else:
            #     print("using naverAPI")
            #     self.newNews = naverAPI.get_news(self.name, begin=method.date_to_str(begin))

            temp = getPrice.stock_price(self.code, begin=self.update_day)
            temp.to_csv("../file/price/"+self.code+".csv", encoding="UTF-8")
            self.newPrice = pd.read_csv("../file/price/"+self.code+".csv", encoding="UTF-8")[['Date', 'High', 'Low', 'Open', 'Close', 'Volume']]
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
            self.model_day1 = modeling.load_model("005930", predict_day=1, features=features)
            # self.model_day1 = modeling.modeling(batch, term, self.features)
            # self.model_day1 = modeling.model_educate(self, term, batch, 1)
            # if len(self.news) < 560:
            #     self.model_day1 = modeling.load_model("005930", predict_day=1, features=self.features)  # 데이터가 부족한 종목의 경우 삼성전자 모델로 예측진행
            # elif not os.path.isfile("model/model_day1/withNews/" + self.code + "/saved_model.pb"):
            #     print("predict 1 day Model Compiling...")
            #     self.model_day1 = modeling.modeling(batch, term, self.features)
            #     self.model_day1 = modeling.model_educate(self, term, batch, 1)
            # else:
            #     self.model_day1 = modeling.load_model(self.code, predict_day=1, features=features)
            #     print("predict 1 day Model load completed!")

            # if not os.path.isfile("model/model_day7/withNews/" + self.code + "/saved_model.pb"):
            #     print("predict 7 days Model Compiling...")
            #     self.model_day7 = modeling.modeling_day7(batch, term, self.features)
            #     self.model_day7 = modeling.model_educate(self, term, batch, 7)
            #     print("predict 7 days Model load completed!")
            #
            # else:
            #     print("Load model..")
            #     self.model_day7 = modeling.load_model(self.code, predict_day=7, features=features)

    def predict_day1(self):
        self.result_day1 = modeling.predict_day1(self)
    # def predict_price_day7(self):
    #     self.result_day7 = modeling.predict_day7(self)

    def test_predict_day1(self):
        return modeling.test_day1(self)

    def result_save(self):
        company = OrderedDict()
        company["name"] = self.name
        company["code"] = self.code
        company['predict'] = int(self.result_day1['Predict'][0][0])
        last_price1 = self.result_day1['Price'][-1]
        rate = 100 * (company['predict'] - last_price1) / last_price1
        company['rate'] = round(rate, 2)

        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$set': company}, db_name=db_name, collection_name="predictResult")

