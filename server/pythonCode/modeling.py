import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint
from silence_tensorflow import silence_tensorflow
import pandas as pd
import numpy as np
from collections import OrderedDict
from . import method
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

silence_tensorflow()

gpus = tf.config.experimental.list_physical_devices('GPU')

early_stop = EarlyStopping(monitor="val_loss", patience=5)

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

def modeling(batch, term, features):
    model = keras.Sequential()
    model.add(keras.layers.LSTM(128, batch_input_shape=(batch, term, features), stateful=True, return_sequences=True))
    model.add(keras.layers.LSTM(128, stateful=True))
    model.add(keras.layers.Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

def modeling_nlp(max_words):
    model = keras.Sequential()
    model.add(keras.layers.Embedding(max_words, 100))
    model.add(keras.layers.LSTM(120))
    model.add(keras.layers.Dense(3, activation="softmax"))
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=['accuracy'])
    return model

def model_educate(company, predict_day, feature, model_type=None):
    model = None
    data = company.price[['Date', 'Close', 'Volume', "EMA"]]

    if feature == 3:
        data = method.merge(company.news, company.price[['Date', "EMA", 'Volume']], "Date", "Date")
    else:
        print("model selecting Error")
    if model_type == 'test':
        model = company.test_model
    elif model_type == "predict":
        model = company.model
    else:
        print("Model selecting Error")
    print(data.isnull().sum())
    data.pop("Date")

    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    data = Scaler.fit_transform(data)
    train_data = data

    if model_type == "test":
        train_data = data[:int(len(data) * 0.7)]
        val_data = data[int(len(data) * 0.7):int(len(data) * 0.8)]
    else:
        val_data = method.sample_data(company.span)
        Scaler.fit(val_data)
        val_data=Scaler.fit_transform(val_data)

    train_x, train_y = create_dataset(train_data, company.term, predict_day)
    batch_point = method.re_sizing(company.batch_size, train_x)
    train_x, train_y = train_x[batch_point:], train_y[batch_point:]

    val_x, val_y = create_dataset(val_data, company.term, predict_day)
    batch_point = method.re_sizing(company.batch_size, val_x)
    val_x, val_y = val_x[batch_point:], val_y[batch_point:]

    print(train_x.shape, train_y.shape)

    if feature == 3 and model_type == "test":
        path = "model/test_model/{}.h5".format(company.code)
        check_point = ModelCheckpoint(path, monitor='val_loss', mode='min', save_best_only=True)
        history = model.fit(train_x, train_y, epochs=100, batch_size=company.batch_size, verbose=0, callbacks=[early_stop, check_point], validation_data=(val_x, val_y))

    elif feature == 3 and model_type == "predict":
        path = "model/{}.h5".format(company.code)
        check_point = ModelCheckpoint(path, monitor='val_loss', mode='min', save_best_only=True)
        history = model.fit(train_x, train_y, epochs=100, batch_size=company.batch_size, verbose=0, callbacks=[early_stop, check_point], validation_data=(val_x, val_y))

    else:
        print("Number of feature setting Error")

    return model

def test(company, features):
    test_model = None
    data = pd.DataFrame()
    if features == 3:
        data = method.merge(company.news, company.price[['Date', "EMA", 'Volume', 'Close']], "Date", "Date")
        test_model = company.test_model
    else:
        print("Model selecting Error")
    data.dropna(inplace=True)
    ma = data['EMA']
    close = data.pop('Close')

    if company.code == "005930":
        data = data[int(len(data)*0.8):]
        close = close[int(len(close)*0.8):]
        ma = ma[int(len(ma)*0.8):]

    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")
    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, company.term, 1)

    timeline = timeline[company.term:]
    close = close[company.term:]
    ma = ma[company.term:]

    batch_point = method.re_sizing(batch_size=10, data=x_data)
    x_data = x_data[batch_point:]

    timeline = timeline[batch_point:]
    close = np.array(close[batch_point:])
    ma = np.array(ma[batch_point:])

    prediction = test_model.predict(x_data, batch_size=company.batch_size)
    real_prediction = method.inverseTransform(Scaler, prediction, features)
    predict_price = []
    for i in range(1, len(real_prediction)):
        predict_price.append(method.ema_to_price(real_prediction[i], ma[i-1], company.span))
    predict_price = np.array(predict_price)
    result = pd.DataFrame({"Date": timeline[1:], "Actual_Price": close[1:], "Predict_Price": predict_price})

    return result

def predict(company, features):
    model = None
    data = pd.DataFrame()
    if features == 3:
        data = method.merge(company.news, company.price[['Date', "EMA", 'Volume', 'Close']], "Date", "Date")
        model = company.model
    else:
        print("Model selecting Error")
    ma = data['EMA']
    close = data.pop('Close')

    timeline = pd.to_datetime(data.pop("Date"), format="%Y-%m-%d")
    Scaler = MinMaxScaler(feature_range=(0, 1))
    Scaler.fit(data)
    normed_data = Scaler.fit_transform(data)
    x_data, y_data = create_dataset(normed_data, company.term, 1)

    timeline = timeline[company.term:]
    close = close[company.term:]
    ma = ma[company.term:]

    batch_point = method.re_sizing(batch_size=10, data=x_data)
    x_data = x_data[batch_point:]

    timeline = timeline[batch_point:]
    close = np.array(close[batch_point:])
    ma = np.array(ma[batch_point:])

    prediction = model.predict(x_data, batch_size=company.batch_size)
    real_prediction = method.inverseTransform(Scaler, prediction, features)
    predict_price = method.ema_to_price(real_prediction[-1], ma[-2], company.span)
    rate = round(100 * (predict_price-close[-1])/close[-1], 2)

    result = OrderedDict()
    result['code'] = company.code
    result['name'] = company.name
    result['predict'] = int(predict_price)
    result['rate'] = rate

    return result

def view_day1(time, actual, predict, name):
    plt.figure(figsize=(16, 9))
    plt.plot(time[:20], actual[-29:-1], label="price")
    plt.scatter(time[20:], actual[-1], label="Actual", edgecolors='k', c='#2ca02c', s=100)
    plt.scatter(time[20:], predict, label="Predict", edgecolors='k', marker='X', c='#ff7f0e', s=100)
    plt.xlabel("Time")
    plt.ylabel("Close Price(KRW)")
    plt.title(name+"'s Predicted next day's Close(￦)")

def view_overall(days, actual, ma, predict, name, features):
    plt.figure(figsize=(16, 9))
    plt.plot(days, actual, label="Actual")
    plt.plot(days, ma, label="EMA")
    plt.plot(days, predict, label="Predict")
    plt.xlabel("Time")
    plt.ylabel("Close(KRW)")
    plt.legend()
    plt.title(name+"\'s Close(KRW) (Feat."+str(features)+")")
    plt.show()

def view_overall2(days, actual, ma, predict_ma, predict_price, name, features):
    plt.figure(figsize=(16, 9))
    plt.plot(days[int(len(days)*0.7):], actual[int(len(days)*0.7):], label="Actual_Price")
    plt.plot(days[int(len(days)*0.7):], predict_price[int(len(days)*0.7):], label="Predict_Price")
    # plt.plot(days, ma, label="EMA")
    # plt.plot(days, predict_ma, label="Predict_EMA")
    plt.xlabel("Time")
    plt.ylabel("Close(KRW)")
    plt.legend()
    plt.title(name+"\'s Close(KRW) (Feat."+str(features)+")")
    plt.show()