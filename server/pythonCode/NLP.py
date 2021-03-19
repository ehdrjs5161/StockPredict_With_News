from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt
import re
import numpy as np
import pandas as pd
from server.pythonCode import modeling
import time
import os

stopwords = [',', '…', '-', '\'', '·', '‘', '\"', '!', '`', '…', '’', '의', '가', '이', '은',
             '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']

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

    train = pd.read_csv("../file/NLP/train_data.csv", encoding="utf-8")[['Title', 'Label']]

    begin = time.time()
    train_x = preprocess(train)
    end = time.time()
    print("predict_method_preprocess Time: ", end - begin, "(sec)")

    max_words = 50000
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

    train_y = np.array(train_y)
    if not os.path.isfile("../model/NLP_model/saved_model.pb"):
        print("dd")
        model = modeling.modeling_nlp(max_words)
        print("model_day1 Setting Completed")
        history = model.fit(train_x, train_y, epochs=10, batch_size=10, validation_split=0.1)
        model.save("../test_result/NLP_model")

    model = load_model("../model/NLP_model")
    print("NLP model load Completed!")
    predict = model.predict(test_x)
    predict_Label = np.argmax(predict, axis=1)
    result = test.assign(Label=predict_Label)

    return result

def predict_prototype(news):
    print("Predict")
    max_len =50

    train = pd.read_csv("../file/NLP/train_data.csv", encoding="utf-8")[['Title', 'Label']]
    test = news

    begin = time.time()
    test_x = preprocess(test)
    end = time.time()
    print("preprocess Time: ", end - begin, "(sec)")

    max_words = 50000
    tokenizer = Tokenizer(num_words=max_words)
    tokenizer.fit_on_texts(test_x)

    test_x = tokenizer.texts_to_sequences(test_x)
    test_x = pad_sequences(test_x, maxlen=max_len)
    if not os.path.isfile("../model/NLP_model/saved_model.pb"):
        model = modeling.modeling_nlp(max_words)
    else:
        model = load_model("../model/NLP_model")
        print("NLP Load Completed!\n")
    label = model.predict(test_x)
    predict_Label = np.argmax(label, axis=1)
    sample = test.assign(Label=predict_Label)

    return sample
