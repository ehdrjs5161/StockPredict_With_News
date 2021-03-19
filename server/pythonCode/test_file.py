import pandas as pd
from server.pythonCode import NLP
from server.pythonCode import sentiment_analysis as sent
import time
if __name__ == "__main__":
    data = pd.read_csv("../file/news/068270.csv")[['Date', 'Title', 'Label']]
    data.drop_duplicates(['Title'], inplace=True)

    data0 = data[['Date', 'Title']]
    result = sent.labeling(data0)
    print("print senti result\n", result)

    begin = time.time()
    result1 = NLP.predict(data0)
    result1.to_csv("../test_result/fit_on_train.csv", encoding="UTF-8")
    end = time.time()
    # print("fit_on_train_data result")
    # print(result1)
    #
    begin2 = time.time()
    result2 = NLP.predict_prototype(data0)
    end2 = time.time()
    # result2.to_csv("../test_result/fit_on_test.csv", encoding="UTF-8")

    print("fit_on_test_data result")
    # print(result2)
    # #
    # result1.to_csv("../test_result/fit_on_train.csv")
    # result2.to_csv("../test_result/fit_on_test.csv")
    # # result = pd.read_csv("../file/news/NLP_result.csv")[['Date', 'Title', 'Label']]
    # # result.drop_duplicates(['Title'], inplace=True)
    # # result2 = pd.read_csv("../file/news/NLP_result2.csv")[['Date', 'Title', 'Label']]
    # # result2.drop_duplicates(['Title'], inplace=True)
    #
    score0 = 0
    score1 = 0
    score2 = 0
    #

    #
    for i in range(0, len(data)):
        if data['Label'].iloc[i] == result['Label'].iloc[i]:
            score0 += 1
        if data['Label'].iloc[i] == result1['Label'].iloc[i]:
            score1 += 1
        if data['Label'].iloc[i] == result2['Label'].iloc[i]:
            score2 += 1

    print("감성사전 이용 실제 값 대비 유사도: ", 100 * score0/len(data), "%")
    begin = time.time()
    re = NLP.preprocess(data0)
    end = time.time()
    print(re, "\n", end-begin)
    print("fit_on_text(train_x) 실제 값 대비 유사도: ", 100 * score1/len(data), "%")
    print("Time: ", end - begin)
    print("fit_on_text(test_x) 실제 값 결과 대비 유사도: ", 100 * score2/len(data), "%")
    print("Time: ", end2 - begin2)
