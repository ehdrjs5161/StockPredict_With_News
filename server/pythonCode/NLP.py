from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt
import re
import numpy as np
import pandas as pd
from pythonCode import modeling
import time
import os

stopwords = [',', '…', '-', '\'', '·', '‘', '\"', '!', '`', '…', '’', '의', '가', '이', '은',
             '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']

def newsLabeling(news):
    result = []
    max_word = 35000
    tokenizer = Tokenizer(num_words=max_word)
    for title in news['Title']:
        title = re.sub('[-=+,~!@#$%^&*>>[]]', '', str(title))
        temp = Okt.morphs(title, stem=True)
        temp = [word for word in temp if not word in stopwords]
        result.append(temp)
    tokenizer.fit_on_texts(result)

def preprocess(data):
    okt = Okt()
    x_data = []
    for title in data['Title']:
        title = re.sub('[-=+,~!@#$%^&*>>[]]', '', str(title))
        temp = okt.morphs(title, stem=True)
        temp = [word for word in temp if not word in stopwords]
        x_data.append(temp)

    return x_data

def predict(news):
    max_len =30
    begin = time.time()
    train = pd.read_csv("../file/NLP/train_data.csv", encoding="utf-8")[['Title', 'Label']]
    train_x = preprocess(train)
    end = time.time()

    max_words = 35000
    tokenizer = Tokenizer(num_words=max_words)
    tokenizer.fit_on_texts(train_x)
    train_x = tokenizer.texts_to_sequences(train_x)
    train_x = pad_sequences(train_x, maxlen=max_len)

    test = news
    test_x = preprocess(test)
    test_x = tokenizer.texts_to_sequences(test_x)
    test_x = pad_sequences(test_x, maxlen=max_len)

    train_y = []

    for i in range(0, len(train['Label'])):
        if train['Label'].iloc[i] == 1:
            train_y.append([0, 0, 1])
        elif train['Label'].iloc[i] == 0:
            train_y.append([0, 1, 0])
        elif train['Label'].iloc[i] == -1:
            train_y.append([1, 0, 0])

    if not os.path.isfile("../model/NLP_model/saved_model.pb"):
        model = modeling.modeling_nlp(max_words)
        print("model_day1 Setting Completed")
        history = model.fit(train_x, train_y, epochs=10, batch_size=10, validation_split=0.1)
        model.save("../NLP_model")

    model = load_model("../model/NLP_model")
    print("NLP model_day1 save Completed!")
    predict = model.predict(test_x)
    predict_Label = np.argmax(predict, axis=1)
    result = test.assign(label=predict_Label)

    return result

def predict_prototype(news):
    print("Predict")
    max_len =30
    begin = time.time()
    train = pd.read_csv("../file/NLP/train_data.csv", encoding="utf-8")[['Title', 'Label']]
    # train_x = preprocess(train)
    end = time.time()
    max_words = 35000
    tokenizer = Tokenizer(num_words=max_words)
    # tokenizer.fit_on_texts(train_x)
    test = pd.read_csv("../file/news/068270.csv", encoding="UTF-8")[["Date", 'Title']]

    test_x = preprocess(test)
    tokenizer.fit_on_texts(test_x)
    test_x = tokenizer.texts_to_sequences(test_x)
    test_x = pad_sequences(test_x, maxlen=max_len)
    if not os.path.isfile("../model/NLP_model/saved_model.pb"):
        model = modeling.modeling_nlp(max_words)
    model = load_model("../model/NLP_model")
    print("NLP Load Completed!\n")
    label = model.predict(test_x)
    predict_Label = np.argmax(label, axis=1)
    sample = test.assign(label=predict_Label)
    sample.to_csv("../predict_method_result.csv", encoding="UTF-8")

if __name__ == "__main__":
    # educate() -> predict 로 변경
    # predict("a") -> predict_prototype 으로 변경
    news = pd.read_csv("../file/news/068270.csv", encoding="UTF-8")[['Date', 'Title', 'Label']]
    sent = pd.read_csv("../file/news/processed_news/068270.csv", encoding="UTF-8")[['Date', 'Title', 'Label']]
    score=0
    for i in range(len(news)):
        if news["Label"].iloc[i] == sent['Label'].iloc[i]:
            score += 1
    print("유사도: ", score/len(news))
    print(news)
    print(sent)
    # sent = pd.read_csv("../analysis.csv", ecoding="UTF-8")[['Title', 'Label']]
    # predict = pd.read_csv("../predict_method_result.csv", encoding="UTF-8")[['Title', 'label']]
    # educate = pd.read_csv("../educate_method_result.csv", encoding="UTF-8")[['Title', 'label']]
    #
    # score1 = 0
    # score2 = 0
    # for i in range(len(sent)):
    #     if sent['Label'].iloc[i] == educate['label'].iloc[i]:
    #         score1 = score1 + 1
    #     if sent['Label'].iloc[i] == predict['label'].iloc[i]:
    #         score2 = score2 + 1
    # print("Compare Educate/Senti: ", score1/len(sent)*100)
    # print("Compare Predict/Senti: ", score2/len(sent)*100)