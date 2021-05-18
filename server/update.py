import pandas as pd
from pythonCode import DB_Handler as DB_Handler
from pythonCode import method as method
from pythonCode import company as company
import datetime
from collections import OrderedDict

mongo = DB_Handler.DBHandler()

def predict(code):
    name = method.code_to_name(kospi, code)
    comp = company.companys(name=name, code=code, batch=10, term=10)
    comp.load_data(10)
    print("-----------------------------------------------------------------------------------------------")
    print("종목코드: ", code, " 기업명: ", name)
    comp.update_data()
    comp.model_setting()
    comp.test_predict()
    comp.predict_stock()
    comp.result_save()
    print(comp.result)

if __name__ == "__main__":
    kospi = mongo.client.get_database("stockpredict").code
    kospi = pd.DataFrame(kospi.find())[['code', 'name']]
    for code in kospi['code']:
            predict(code)
