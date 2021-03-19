import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from . import method
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
import cufflinks as cf
cf.go_offline(connected=True)

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_memory_growth(gpus[0], True)
  except RuntimeError as e:
    print(e)

def create_dataset(data, term, predict_days):
    x_list, y_list = [], []
    for i in range(len(data) - (term + predict_days)+1):
        x_list.append(data[i:(i+term), 0:])
        y_list.append(data[i+term:(i+term+predict_days), 0])
    x_ary = np.array(x_list)
    y_ary = np.array(y_list)
    x_ary = np.reshape(x_ary, (x_ary.shape[0], x_ary.shape[1], x_ary.shape[2]))

    return x_ary, y_ary

def load_model(code, predict_day, features):
    print(code, predict_day)
    try:
        if features == 2:
            if predict_day == 1:
                model = keras.models.load_model("model/model_day1/"+code)
            elif predict_day == 7:
                model = keras.models.load_model("model/model_day7/"+code)
            else:
                print("Deep Learning Model Not Found Error")
        else:
            if predict_day == 1:
                model = keras.models.load_model("model/model_day1/withNews/" + code)
            elif predict_day == 7:
                model = keras.models.load_model("model/model_day7/withNews/" + code)
            else:
                print("Deep Learning Model Not Found Error")

        return model

    except FileNotFoundError as e:
        print(e)
        print("Deep Learning Model Not Found Error")

def modeling(batch, term, features):
    model = keras.Sequential()
    model.add(keras.layers.LSTM(320, batch_input_shape=(batch, term, features), return_sequences=True))
    model.add(keras.layers.LSTM(320))
    model.add(keras.layers.Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

def modeling_day7(batch, term, features):
    model = keras.Sequential()
    model.add(keras.layers.LSTM(512, batch_input_shape=(batch, term, features), return_sequences=True))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.LSTM(512))
    model.add(keras.layers.Dense(7, activation='linear', kernel_initializer=tf.initializers.zeros))
    model.compile(optimizer='adam', loss='mse')
    return model

def modeling_nlp(max_words):
    model = keras.Sequential()
    model.add(keras.layers.Embedding(max_words, 100))
    model.add(keras.layers.LSTM(128))
    model.add(keras.layers.Dense(3, activation="softmax"))
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=['accuracy'])
    return model

def model_educate(company, term, batch, predict_day):
    try:
        if predict_day == 1:
            model = company.model_day1
        elif predict_day == 7:
            model = company.model_day7
    except:
        print("Model Setting Error")

    # print(data)
    if company.features == 2:
        data = company.price[['Date', 'Close', 'Volume']]
    elif company.features == 3:
        news = method.sent_result(company.news[['Date', 'Label']])
        data = method.merge(news, company.price[['Date', 'Close', 'Volume']], "Date", "Date")
    data = data[:int(len(data)*0.9)]
    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")
    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    data = Scaler.fit_transform(data)

    train_data = data[:int(len(data) * 0.9)]

    train_x, train_y = create_dataset(train_data, term, predict_day)
    batch_point = method.re_sizing(batch, train_x)
    train_x = train_x[batch_point:]
    train_y = train_y[batch_point:]

    print(train_x.shape, train_y.shape)

    if company.features == 2:
        if predict_day == 1:
            history = model.fit(train_x, train_y, epochs=50, batch_size=batch, verbose=0)
            model.save("model/model_day1/"+company.code)
        elif predict_day==7:
            history = model.fit(train_x, train_y, epochs=50, batch_size=batch)
            model.save("model/model_day7/" + company.code)
    else:
        if predict_day == 1:
            history = model.fit(train_x, train_y, epochs=50, batch_size=batch)
            model.save("model/model_day1/withNews/" + company.code)
        elif predict_day == 7:
            history = model.fit(train_x, train_y, epochs=50, batch_size=batch)
            model.save("model/model_day7/withNews/" + company.code)
        else:
            print("predict_day Setting Error!")

    plt.figure(figsize=(16, 9))
    plt.plot(history.history['loss'], label="loss")
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.legend()
    plt.show()


    return model

def update_model(company):
    model_day1 = company.model_day1
    model_day7 = company.model_day7

    return model_day1, model_day7

def test_day1(company):
    model = company.model_day1
    if company.features == 2:
        data = company.price[['Date', 'Close', 'Volume']]
    elif company.features == 3:
        news = method.sent_result(company.news[['Date', 'Label']])
        data = method.merge(news, company.price[['Date', 'Close', 'Volume']], "Date", "Date")
    print(len(data))
    price = data['Close']
    time = data['Date']
    data = data[int(len(data)*0.9):]

    close = data['Close']
    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")

    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, 28, 1)

    timeline = timeline[28:]
    close = close[28:]

    predictions = model.predict(x_data, batch_size=1)
    real_prediction = method.inverseTransform(Scaler, predictions, features=company.features)

    time = []
    for i in range(0, len(timeline)):
        time.append(method.date_to_str(timeline.iloc[i]))
    result = {'Time': timeline, 'Price': close, 'Predict': real_prediction}
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=timeline[:28], y=price, mode='lines', name="price"))
    # fig.add_trace(go.Scatter(x=timeline[29:], y=close[29:], mode="lines", name="Actual"))
    # fig.add_trace(go.Scatter(x=timeline[29:], y=real_prediction, mode="lines", name="Predict"))
    # fig.update_layout(title='<b>Stock Predict</b>')
    # fig.show()
    score = model.evaluate(x_data, y_data, batch_size=1)
    print(score)
    view_overall(timeline, close, real_prediction, company.name)

def test_day7(company):
    model = company.model_day7
    if company.features == 2:
        data = company.price[['Date', 'Close', 'Volume']]
    elif company.features == 3:
        news = method.sent_result(company.news[['Date', 'Label']])
        data = method.merge(news, company.price[['Date', 'Close', 'Volume']], "Date", "Date")
    price = data['Close']
    time = data['Date']
    data = data[int(len(data) * 0.9):]
    close = data['Close']
    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")

    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, 28, 7)
    timeline = timeline[28:]
    close = close[28:]
    predictions = model.predict(x_data, batch_size=1)
    real_prediction = method.inverseTransform(Scaler, predictions, features=company.features)

    time = []
    for i in range(0, len(timeline)):
        time.append(method.date_to_str(timeline.iloc[i]))
    result = {'Time': timeline, 'Price': close, 'Predict': real_prediction}
    score = model.evaluate(x_data, y_data, batch_size=1)
    print(score)
    # view_overall(timeline, actual=price, predict=real_prediction, name=company.name)
    # print(len(timeline), len(close), len(real_prediction))
    # view_day7(timeline, close, real_prediction, company.name)

def predict_day1(company):
    model = company.model_day1
    if company.features == 2:
        data = company.price[['Date', 'Close', 'Volume']]
    elif company.features == 3:
        news = method.sent_result(company.news[['Date', 'Label']])
        data = method.merge(news, company.price[['Date', 'Close', 'Volume']], "Date", "Date")

    data = data[-29:]
    # data = data[['Date', 'Close', 'Volume']]
    close = list(data['Close'])
    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")

    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, 28, 1)
    predictions = model.predict(x_data, batch_size=1)
    real_prediction =method.inverseTransform(Scaler, predictions)
    real_prediction = list(real_prediction)

    time = []
    for i in range(0, len(timeline)):
        time.append(method.date_to_str(timeline.iloc[i]))
    result = {'Time': time, 'Price': close, 'Predict': real_prediction}
    # view_day1(time, close, real_prediction, company.name)
    # view_overall(time, close, real_prediction, company.name)
    return result

def predict_day7(company):
    model = company.model_day7
    if company.features == 2:
        data = company.price[['Date', 'Close', 'Volume']]
    elif company.features == 3:
        news = method.sent_result(company.news[['Date', 'Label']])
        data = method.merge(news, company.price[['Date', 'Close', 'Volume']], "Date", "Date")
    data = data[-35:]
    # data = data[['Date', 'Close', 'Volume']]
    close = list(data['Close'])
    # data = method.merge(company.news, company.price, "Date", "Date")
    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")

    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, 28, 7)

    predictions = model.predict(x_data, batch_size=1)
    real_prediction = method.inverseTransform(Scaler, predictions, features=company.features)
    real_prediction = list(real_prediction)
    time =[]
    for i in range(0, len(timeline)):
        time.append(method.date_to_str(timeline.iloc[i]))
    result = {'Time': time, 'Price': close, 'Predict': real_prediction}
    view_day7(time, close, real_prediction, company.name)
    return result

def view_day1(time, actual, predict, name):
    plt.figure(figsize=(18, 9))
    plt.plot(time[:28], actual[-29:-1], label="price")
    plt.scatter(time[28:], actual[-1], label="Actual", edgecolors='k', c='#2ca02c', s=100)
    plt.scatter(time[28:], predict, label="Predict", edgecolors='k', marker='X', c='#ff7f0e', s=100)
    plt.xlabel("Time")
    plt.ylabel("Close Price(KRW)")
    plt.title(name+"'s Predicted next day's Close(￦)")
    plt.legend()
    plt.show()

def view_day7(days, actual, predict, name):
    plt.figure(figsize=(18, 9))
    plt.plot(days[:28], actual[:28], label="price")
    plt.scatter(days[28:], actual[28:], label="Actual", edgecolors='k', c='#2ca02c', s=100)
    plt.scatter(days[28:], predict, label="Predict", edgecolors='k', marker='X', c='#ff7f0e', s=100)
    plt.xlabel("Time")
    plt.ylabel("Close Price(KRW)")
    plt.legend()
    plt.title(name+"'s Predicted next week's Close(￦)")
    plt.show()

def view_overall(days, actual, predict, name):
    plt.figure(figsize=(16, 9))
    plt.plot(days, actual, label="Actual")
    plt.plot(days, predict, label="Predict")
    plt.xlabel("Time")
    plt.ylabel("Close(KRW)")
    plt.legend()
    plt.title(name+"s Close(KRW)")
    plt.show()

def view_overallDay7(days, actual, predict, name):
    plt.figure(figsize=(16, 9))
    plt.plot(days, actual, label="Actual")
    plt.plot(days, predict, label="Predict")
