import pandas as pd
from tensorflow import keras
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
        self.newNews = None
        self.newPrice = None
        self.batch_size = None
        self.term = None
        self.test_model= None
        self.model = None
        self.test_result = None
        self.result = None
        self.span = None

    def load_data(self, span):
        self.span = span
        self.news, self.price = method.load_data(self)

    def update_data(self):
        yesterday = method.date_to_str(datetime.datetime.today()-datetime.timedelta(days=1))
        yesterday = method.str_to_date(yesterday)
        # 가지고 있는 뉴스 데이터의 마지막 날짜와 어제 날짜를 비교하여 뉴스 데이터 중 어제 뉴스가 포함되지 않다면 크롤링해서 저장.
        if method.str_to_date(self.news['Date'].iloc[-1]) != yesterday:
            print("Update News")
            begin = method.str_to_date(self.news['Date'].iloc[-1]) + datetime.timedelta(days=1)
            self.newNews = getNews.crawling(name=self.name, begin=method.date_to_str(begin), end=method.date_to_str(yesterday))
            print(len(self.newNews))
            if len(self.newNews) > 0:
                self.newNews = method.sent_result(self.newNews[['Date', 'Label']])
                newNews = method.csv_to_json(self.newNews)
                print(newNews)
                for news in newNews:
                    mongo.update_item(condition={"code": "{}".format(self.code)},
                                      update_value={'$push': {'news': news}}, db_name=db_name, collection_name="news")
                self.news = pd.concat([self.news, self.newNews])

        if method.str_to_date(self.price['Date'].iloc[-1]) != yesterday:
            print("Update Price")
            temp = getPrice.stock_price(self.code, begin=self.price['Date'].iloc[-1])
            temp.to_csv("file/price/"+self.code+".csv", encoding="UTF-8")
            self.newPrice = pd.read_csv("file/price/"+self.code+".csv", encoding="UTF-8")[['Date', 'High', 'Low', 'Open', 'Close', 'Volume']]
            newPrice = method.csv_to_json(self.newPrice)

            for price in newPrice:
                mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$push': {'price': price}}, db_name=db_name, collection_name="price")

            self.price = pd.concat([self.price, self.newPrice])

        else:
            print(self.name+"'s News & Price data are already Updated!")

    def model_setting(self, batch, term):
        self.batch_size = batch
        self.term =term
        if not os.path.isfile("model/test_model/{}.h5".format(self.code)):
            print("Create Test Model")
            if len(self.news) < 1000:
                if os.path.isfile("model/test_model/005930.h5"):
                    self.test_model = keras.models.load_model("model/test_model/005930.h5")
                else:
                    print("For predicting company whose low length data , Save Samsung Electric model First")
                print("Because of pool data length use Samsung model")
            else:
                self.test_model = modeling.modeling(batch, term, features=3)
                self.test_model = modeling.model_educate(self, 1, feature=3, model_type="test")
                print("Test_model educate: Completed")
        else:
            self.test_model = keras.models.load_model("model/test_model/{}.h5".format(self.code))
            print("Test_model load: Completed!")

        if not os.path.isfile("model/{}.h5".format(self.code)):
            print("Create Model")
            self.model = modeling.modeling(batch, term, features=3)
            self.model = modeling.model_educate(self, 1, feature=3, model_type="predict")
            print("Model educate: Completed")
        else:
            self.model = keras.models.load_model("model/{}.h5".format(self.code))
            print("Model load: completed!")

    def predict_stock(self):
        self.result = modeling.predict(self, features=3)

    def test_predict(self):
        self.test_result = modeling.test(self, features=3)

    def result_save(self):
        temp = OrderedDict()
        temp['code'] = self.code
        temp['price'] = method.csv_to_json(self.test_result)
        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$set': temp}, db_name=db_name, collection_name="testResult")
        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={"$set": self.result}, db_name=db_name, collection_name="predictResult")
