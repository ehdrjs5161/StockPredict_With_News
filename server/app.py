from flask import Flask, request, jsonify
import pandas as pd
import pythonCode.DB_Handler as DB_Handler
import pythonCode.method as method
import pythonCode.company as company
import datetime
from collections import OrderedDict
mongo = DB_Handler.DBHandler()

app = Flask(__name__, static_folder='server/pythonCode')
app.config['JSON_AS_ASCII'] = False

@app.route('/code', methods=['GET', 'POST'])
def code_list():
    kospi = mongo.find_items(db_name="stockPredict", collection_name="code")
    kospi = pd.DataFrame(kospi)[['code', 'name']]
    kospi = kospi.to_dict("records")
    code_data = OrderedDict()
    code_data['list'] = kospi
    return code_data


@app.route('/code/<code>', methods=['GET', 'POST'])
def predict(code):
    kospi = mongo.find_items(db_name="stockPredict", collection_name="code")
    kospi = pd.DataFrame(kospi)[['code', 'name']]
    name = method.code_to_name(kospi, code)
    comp = company.companys(name=name, code=code)
    comp.load_data()
    update = method.date_to_str(datetime.datetime.today() - datetime.timedelta(days=1))
    print(update, comp.update_day)

    if update == comp.update_day:
        # comp.update_data()
        print(len(comp.news), len(comp.price))
        comp.model_setting(10, 28, 2)
        comp.test_predict_day7()
        comp.model_setting(10, 28, 3)
        comp.test_predict_day7()
        # comp.result_save()

    result = mongo.find_item(condition={"code": "{}".format(comp.code)}, db_name="stockPredict", collection_name="predictResult")
    del result['_id']
    temp = OrderedDict()
    temp['code'] = result['code']
    temp['name'] = result['name']
    price = []
    date = []
    for p in result['price_day1']:
        price.append(int(p['Price']))
        date.append(p['Date'])
    temp['price'] = price
    temp['date'] = date
    return result

@app.route('/rank', methods=['GET', 'POST'])
def rank():
    cursor = mongo.find_items(db_name="stockPredict", collection_name="rank")
    result = OrderedDict()
    result_list=[]
    for rank in cursor:
        del rank['_id']
        result_list.append(rank)
    result['result'] = result_list
    return result

if __name__ == "__main__":
    code_list()