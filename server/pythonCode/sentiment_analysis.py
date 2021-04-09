import pandas as pd
import codecs
import re

def set_word_list():
    positive = []
    negative = []
    total = []
    pos = codecs.open("../file/NLP/positive_words_self.txt", 'rb', encoding="UTF-8")

    while True:
        line = pos.readline()
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        positive.append(line)
        total.append(line)
        if not line:
            break
    pos.close()

    neg = codecs.open("../file/NLP/negative_words_self.txt", 'rb', encoding="UTF-8")

    while True:
        line = neg.readline()
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        negative.append(line)
        total.append(line)
        if not line:
            break
    neg.close()

    return positive, negative, total

def isin(title, total):
    for word in total:
        if word in title:
            return True
    return False

def analysis(title, positive, negative, total):
    sent = 0
    if not isin(title, total):
        return 0
    for word in positive:
        if word in title:
            sent = sent + 1
    for word in negative:
        if word in title:
            sent = sent - 1
    return sent

def classify(sent):
    if sent > 0:
        return 2
    elif sent < 0:
        return 0
    else:
        return 1

def labeling(news):
    pos, neg, total= set_word_list()
    label = []
    titles = news['Title']
    for i in range(0, len(titles)):
        title = news['Title'].iloc[i]
        title = re.sub('[]\"\"''[]', '', title)
        sent = analysis(title, pos, neg, total)
        label.append(classify(sent))
    news = pd.DataFrame({'Date': news['Date'], 'Title': titles, 'Label': label})
    return news