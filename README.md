# 프로젝트 개요 (Overview)
뉴스 데이터를 기반으로 하여 KOSPI 200 주식 종목의 종가를 예측하는 웹 서비스 입니다.


# 프레임 워크 & 라이브러리 (Frame Work & Library)

* Beautiful-Soup

* pandas_datareader

* TensorFlow

* Flask

* React.js

* numpy

* ...

# 데이터 (Data)

* Beautiful-Soup를 이용하여 수집한 2012년 1월 1일 이후 뉴스의 헤드라인 데이터
  
* pandas_datareader를 이용하여 수집한 2012년 1월 1일 이후 KOSPI 200의 상위 100개 종목의 주식데이터
  
# 자연어 처리(Natural Language Processing)

* 창원대학교 적응지능연구실에서 제공한 형용사 긍/부정 감성사전과 주식 관련 명사 감성사전을 이용하여 뉴스의 헤드라인을 긍정, 중립, 부정으로 분류

* 감성분석 결과 값은 하루동안 작성된 뉴스들의 값에 대한 평균으로 주식 데이터와 동기화 작업 진행 후 사용
  
# 딥러닝 (Deep Learning)
 
* 딥러닝의 Features 선정 방법: 상관계수, VIF(Variance Inflation Factor) 사용

* 케라스를 이용한 LSTM모델로 이전 28일의 종가, 거래량, 뉴스 감성분석 값을 Features로 하여 다음 개장일의 종가(Close)를 예측

# 웹 (Web)

* python 기반의 코드 실행을 위해 Flask로 서버 구축

* React.js를 이용하여 UI 제공

