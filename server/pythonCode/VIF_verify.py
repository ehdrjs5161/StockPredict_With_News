import json
from collections import OrderedDict
import pandas as pd
from pythonCode import NLP
from pythonCode import sentiment_analysis as sent
from statsmodels.stats.outliers_influence import variance_inflation_factor
import seaborn as sns
from matplotlib import pyplot as plt

if __name__ =="__main__":
    data = pd.read_csv("../test_data.csv")[['Close', 'Volume', 'Label']]
    print(data)
    vif = pd.DataFrame()
    vif['VIF Factor'] = [variance_inflation_factor(data.values, i) for i in range(data.shape[1])]
    vif['Features'] = data.columns
    print(vif)

    cmap = sns.light_palette("gray", as_cmap=True)
    sns.heatmap(data.corr(), annot=True, cmap=cmap)
    plt.show()