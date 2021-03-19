import pandas as pd
from server.pythonCode import method
from statsmodels.stats.outliers_influence import variance_inflation_factor
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

news = pd.read_csv("../file/news/068270.csv")[['Date', 'Title', 'Label']]
news.drop_duplicates(['Title'], inplace=True)
news = method.sent_result(news[['Date', 'Label']])
price = pd.read_csv("../file/price/068270.csv")[['Date', 'Close', 'Volume']]

data = method.merge(news, price, col1='Date', col2='Date')
data.pop('Date')


# Scaler = MinMaxScaler(feature_range=(0, 1))
# Scaler.fit(data)
# data = Scaler.fit_transform(data)
# print(type(data), data.shape)
# close = []
# volume = []
# label = []
#
# for row in data:
#     close.append(row[0])
#     volume.append(row[1])
#     label.append(row[2])
#
# data = pd.DataFrame({'Close': close, 'Volume': volume, 'Label': label})

if __name__ =="__main__":
    print(data)
    vif = pd.DataFrame()
    vif['VIF Factor'] = [variance_inflation_factor(data.values, i) for i in range(data.shape[1])]
    vif['Features'] = data.columns
    print(vif)

    cmap = sns.light_palette("gray", as_cmap=True)
    sns.heatmap(data.corr(), annot=True, cmap=cmap)
    plt.show()
