import pandas as pd
from server.pythonCode import DB_Handler as DB_Handler
from server.pythonCode import method as method
from server.pythonCode import company as company
import datetime
from collections import OrderedDict

mongo = DB_Handler.DBHandler()

def predict(code):
    name = method.code_to_name(kospi, code)
    comp = company.companys(name=name, code=code)
    comp.load_data(10)
    print("-----------------------------------------------------------------------------------------------")
    print("종목코드: ", code, " 기업명: ", name)

    # features=3 news, 20MA or EWM, volume
    # features=6 news, 20MA or EWM, volume, BPS, PER, PBR, EPS

    comp.update_data()
    comp.model_setting(10, 10)
    comp.test_predict()
    comp.predict_stock()
    print(comp.result)
    comp.result_save()

if __name__ == "__main__":
    kospi = mongo.find_items(db_name="stockPredict", collection_name="code")
    kospi = pd.DataFrame(kospi)[['code', 'name']]

    for i in range(44, len(kospi['code'])):
        predict(kospi['code'].iloc[i])
