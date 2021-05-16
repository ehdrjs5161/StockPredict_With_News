# 개요 (Overview)
뉴스 데이터를 기반으로 하여 KOSPI 200 상위 100개 종목의 종가를 예측하는 웹 어플리케이션


# 프레임 워크 & 라이브러리

* python 3.6

* beautiful-Soup

* pandas_datareader

* pymongo

* dnspython

* tensorflow-gpu==2.4

* numpy

* sklearn

* plotly

* dash
 
* dash_core_components

* dash_html_components

* ...

```
# pip이 설치되어 있다면 아래의 명령어로 라이브러리를 설치할 수 있다.
pip install [Library_name]
```

# 데이터

* Beautiful-Soup를 이용하여 수집한 2012년 1월 1일 이후 네이버 뉴스의 헤드라인 데이터
  
* pandas_datareader를 이용하여 수집한 2012년 1월 1일 이후 KOSPI 200의 상위 100개 종목의 주식데이터(OHLCV)

* MongoDB에 각 기업의 종목코드, 주가데이터, 뉴스데이터, 주가지수, 예측결과 저장.
  
# 감성분석

* 창원대학교 적응지능연구실에서 제공한 형용사 긍/부정 감성사전과 주식 관련 명사 감성사전을 이용하여 뉴스의 헤드라인을 긍정, 중립, 부정으로 분류

* 감성분석 결과 값은 하루동안 작성된 뉴스들의 값에 대한 평균으로 주식 데이터와 동기화 작업 진행 후 사용
  
# 딥러닝
 
* 딥러닝의 Features 선정 방법: 상관계수, VIF(Variance Inflation Factor) 사용

* 케라스를 이용한 LSTM모델로 이전 10일 동안의 10일간 지수이동평균, 거래량, 뉴스 감성분석을 Features로 하여 다음 개장일의 종가(Close)를 예측

* Overfitting현상, Lagging현상을 보완하기 위해 모델 앙상블(Ensemble) 기법 사용.

# 결과

* plotly와 dash를 이용한 그래프 시각화 

* 종목별 예측결과, 테스트 그래프 제공

# 실행

`````
    # 최신 데이터로 업데이트를 위해 update.py 실행
    python update.py

    # plotlyApp.py 실행
    python plotlyApp.py
`````
