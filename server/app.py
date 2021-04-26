from flask import Flask, request, jsonify
import pandas as pd
from pythonCode import DB_Handler as DB_Handler
from pythonCode import method as method
from pythonCode import company as company
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
    print("---------------------------------------------------------------------------")
    print(code)
    print(update, comp.update_day)

    if update != comp.update_day:
        # comp.update_data()
        comp.model_setting(10, 28, 3)
        frame = comp.test_predict_day1()
        frame = method.csv_to_json(frame)
        temp = OrderedDict()
        temp['code'] = code
        temp['result'] = frame
        # print(temp)
        mongo.update_item(condition={"code": "{}".format(code)}, update_value={'$set': temp}, db_name="stockPredict", collection_name="testResult")
    # result = mongo.find_item(condition={"code": "{}".format(comp.code)}, db_name="stockPredict", collection_name="predictResult")
    # del result['_id']
    #
    # return result

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
    kospi = mongo.find_items(db_name="stockPredict", collection_name="code")
    kospi = pd.DataFrame(kospi)[['code', 'name']]
    for code in kospi['code']:
        predict(code)