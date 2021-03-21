import pandas as pd
from collections import OrderedDict
from server.pythonCode import DB_Handler

mongo = DB_Handler.DBHandler()
db_name = "stockPredict"

def set_code(code):
    code = str(code)
    if len(code) < 6:
        for j in range(0, 6 - len(code)):
            code = '0' + code
    return code

def csv_to_json(data):
    return data.to_dict("records")

if __name__ == "__main__":
    # print("a")
    # news = pd.read_csv("../file/news/068270.csv")[['Date', 'Title', 'Label']]
    # pre = news[int(len(news)*0.99):int(len(news)*0.995)]
    # next = news[int(len(news)*0.995):]
    # frame = pd.concat([pre, next])
    # print(len(frame))
    # pre = csv_to_json(pre)
    # next = csv_to_json(next)
    # temp = OrderedDict()
    # temp['code'] = '068270'
    # temp['news'] = pre
    # # 최초로 넣는 부분
    # # i = mongo.insert_item(data=temp, db_name=db_name, collection_name="testnews")
    # # result = mongo.find_item(condition={"code": "068270"}, db_name="stockPredict", collection_name="testnews")
    # # result = pd.DataFrame(result['news'])
    # #
    # # print(result)
    # # print(len(result))
    #
    # # 뉴스 업데이트 시 반복구조
    # # for news in next:
    # #     mongo.update_item(condition={"code": "068270"}, update_value={'$push': {'news': news}}, db_name=db_name, collection_name="testnews")
    # #     print(news)
    # #
    # # result2 = mongo.find_item(condition={"code": "068270"}, db_name="stockPredict", collection_name="testnews")
    # # result2 = pd.DataFrame(result2['news'])
    # # print(result2)
    # mongo.delete_item(condition={"code": "068270"}, db_name=db_name, collection_name="price")
    data = pd.read_csv("../file/KOSPI200.csv")[['종목코드', '기업명']]
    data = data.rename(columns={'종목코드': 'code', '기업명': "name"})
    result = data
    for i in range(0, len(data)):
        result['code'].iloc[i] = set_code(data.iloc[i]['code'])
    # print(result)
    result = result.to_dict("records")
    print(result)
    mongo.insert_items(datas=result, db_name=db_name, collection_name="code")