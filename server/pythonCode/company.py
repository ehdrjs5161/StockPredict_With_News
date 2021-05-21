import pandas as pd
from tensorflow import keras
import datetime
from . import modeling, method, getNews, getPrice, DB_Handler
import os
from collections import OrderedDict

mongo = DB_Handler.DBHandler()
db_name = "stockpredict"

class companys:
    def __init__(self, code, name, batch, term):
        self.code = code
        self.name = name
        self.batch_size = batch
        self.term = term
        self.news =None
        self.price = None
        self.newNews = None
        self.newPrice = None
        self.test_model= None
        self.model = None
        self.test_result = None
        self.result = None
        self.span = None
        self.update = False

    def load_data(self, span):
        self.span = span
        self.news, self.price = method.load_data(self)

    def predict_stock(self):
        self.result = modeling.predict(self, features=3)

    def test_predict(self):
        self.test_result = modeling.test(self, features=3)

    def update_data(self):
        yesterday = method.date_to_str(datetime.datetime.today()-datetime.timedelta(days=1))
        yesterday = method.str_to_date(yesterday)
        # 가지고 있는 뉴스 데이터의 마지막 날짜와 어제 날짜를 비교하여 뉴스 데이터 중 어제 뉴스가 포함되지 않다면 크롤링해서 저장. 토, 일엔 주가 데이터가 나오지 않으므로 뉴스도 업데이트 x
        if method.str_to_date(self.news['Date'].iloc[-1]) != yesterday and method.not_update_day(yesterday):
            print("Update News")
            begin = method.str_to_date(self.news['Date'].iloc[-1]) + datetime.timedelta(days=1)
            self.newNews = getNews.crawling(name=self.name, begin=method.date_to_str(begin), end=method.date_to_str(yesterday))
            print(len(self.newNews))
            if len(self.newNews) > 0:
                self.newNews = method.sent_result(self.newNews[['Date', 'Label']])
                newNews = method.csv_to_json(self.newNews)
                for news in newNews:
                    mongo.update_item(condition={"code": "{}".format(self.code)},
                                      update_value={'$push': {'news': news}}, db_name=db_name, collection_name="news")
                self.news = pd.concat([self.news, self.newNews])
            self.update = True

        if method.str_to_date(self.price['Date'].iloc[-1]) != yesterday:
            print("Update Price")
            begin = method.str_to_date(self.price['Date'].iloc[-1]) + datetime.timedelta(days=1)
            temp = getPrice.stock_price(self.code, begin=method.date_to_str(begin))
            temp.to_csv("file/price/"+self.code+".csv", encoding="UTF-8")
            self.newPrice = pd.read_csv("file/price/"+self.code+".csv", encoding="UTF-8")[['Date', 'Open', 'High', "Low", 'Close', 'Volume']]
            newPrice = method.csv_to_json(self.newPrice)

            for price in newPrice:
                mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$push': {'price': price}}, db_name=db_name, collection_name="price")

            if self.price['Date'].iloc[-1] != self.newPrice['Date'].iloc[0]:
                self.price = pd.concat([self.price, self.newPrice])
            self.price.drop_duplicates(inplace=True)
            self.update = True
        else:
            print(self.name+"'s News & Price data are already Updated!")

        self.price = method.transform(self.price, span=10)
        print(self.price.tail(10))
        if self.update:
            self.model_update()
        else:
            if not os.path.isfile("model/{}.h5".format(self.code)):
                self.model_update()
            else:
                self.model = keras.models.load_model("model/{}.h5".format(self.code))
        self.model_update()

    def model_setting(self):
        if not os.path.isfile("model/test_model/{}.h5".format(self.code)):
            print("Create Test Model")
            if len(self.news) < 1000:
                if os.path.isfile("model/test_model/005930.h5"):
                    self.test_model = keras.models.load_model("model/test_model/005930.h5")
                else:
                    print("For predicting company whose low length data , Save Samsung Electric model First")
                print("Because of pool data length use Samsung model")
            else:
                self.test_model = modeling.modeling(self.batch_size, self.term, features=3)
                self.test_model = modeling.model_educate(self, 1, feature=3, model_type="test")
                print("Test_model educate: Completed")
        else:
            self.test_model = keras.models.load_model("model/test_model/{}.h5".format(self.code))

    def model_update(self):
        print("Create Full data Learning Model")
        self.model = modeling.modeling(self.batch_size, self.term, features=3)
        self.model = modeling.model_educate(self, 1, feature=3, model_type="predict")
        print("Model educate: Completed")

    def result_save(self):
        temp = OrderedDict()
        temp['code'] = self.code
        temp['price'] = method.csv_to_json(self.test_result)
        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={'$set': temp}, db_name=db_name, collection_name="testResult")
        mongo.update_item(condition={"code": "{}".format(self.code)}, update_value={"$set": self.result}, db_name=db_name, collection_name="predictResult")
