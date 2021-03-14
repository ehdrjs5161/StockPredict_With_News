from bs4 import BeautifulSoup
import requests
import pandas as pd

def crawling_kospi():
    codes = []
    names = []
    frame = pd.DataFrame()
    for i in range(1, 21):
        temp = pd.DataFrame()
        url = ("https://finance.naver.com/sise/entryJongmok.nhn?&page={}".format(i))
        source = requests.get(url)
        soup = BeautifulSoup(source.content, "html.parser")
        html = soup.select(".ctg")
        for tag in html:
            code = tag.find("a")['href']
            name = tag.getText()
            code = code[-6:]
            codes.append(code)
            names.append(name)
    result = pd.DataFrame({'종목코드': codes, '기업명': names})
    result.to_csv("./file/KOSPI200.csv", encoding="UTF-8")
    print("KOSPI200 data list Download completed!")
