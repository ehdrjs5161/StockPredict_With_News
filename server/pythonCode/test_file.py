import pandas as pd

if __name__ == "__main__":
    data = pd.read_csv("../file/news/068270.csv")[['Date', 'Title']]
    print(len(data))
    data.drop_duplicates(['Title'], inplace=True)
    print(len(data))
    # result = NLP.predict(data)
    # result = pd.read_csv("../file/news/NLP_result.csv")[['Date', 'Title', 'Label']]
    # result.columns = [['Date', 'Title', 'Label']]
    # result.to_csv("../file/news/NLP_result.csv")
    # print(result)