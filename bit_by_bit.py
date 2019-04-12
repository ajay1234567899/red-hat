from flask import Flask
from flask import render_template
from flask import request
import nltk as n
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import math
import random

app = Flask(__name__)

model = load_model('./model_num_latest.hdf5')

words = pd.read_csv("./scores_latest.csv")

data = {0.8: {},
        0.6: {},
        0.4: {},
        0.2: {},
        0: {},
        -0.2: {},
        -0.4: {},
        -0.6: {},
        -0.8: {},
        -1: {}}
# params
pos = 0.2
neg = 0.2

# put the path sidarth
data1 = pd.read_csv('./Sentiment.csv')
# Keeping only the neccessary columns
data1 = data1[['text', 'sentiment']]

tokenizer = Tokenizer(num_words=8000, split=' ')
tokenizer.fit_on_texts(data1['text'].values)

for j in range(len(words)):
    i = words["words"][j]
    i = i.lower()
    score = words["sentiment"][j]
    if score > 0.8:
        data[0.8][i] = 0
    elif score > 0.6:
        data[0.6][i] = 0
    elif score > 0.4:
        data[0.4][i] = 0
    elif score > 0.2:
        data[0.2][i] = 0
    elif score > 0.0:
        data[0.0][i] = 0
    elif score > -0.2:
        data[-0.2][i] = 0
    elif score > -0.4:
        data[-0.4][i] = 0
    elif score > -0.6:
        data[-0.6][i] = 0
    elif score > -0.8:
        data[-0.8][i] = 0
    elif score > -1:
        data[-1][i] = 0


def sent_analyse(l):
    twt = l
    neg = ['not', 'wont', 'won\'t', 'shouldnt', 'shouldn\'t', 'couldnt', 'couldn\'t']
    flag = 0
    res = []
    for i in twt:
        for j in i.split():
            if j.lower() not in neg:
                res.append(j.lower())
            else:
                flag = 1
    print(res)

    # twt = filtered_sentence
    # vectorizing the tweet by the pre-fitted tokenizer instance
    #   print(res)
    twt = res
    twt = tokenizer.texts_to_sequences(twt)
    #   print(twt)
    # padding the tweet to have exactly the same shape as `embedding_2` input
    twt = pad_sequences(twt, maxlen=41, dtype='int32', value=0)
    sentiment = model.predict(twt, batch_size=1, verbose=2)[0]
    #   print(sentiment)
    #   print('Sentiment:', end='')
    #   if(np.argmax(sentiment) == 0):
    #       print("negative")
    #   elif (np.argmax(sentiment) == 1):
    #       print("positive")
    a, b = sentiment
    #   print(a+b)
    #   print(flag)
    if flag:
        a, b = b, a
    #   print(a, b)
    if a > b:
        return (-(a - .50) / .50)
    elif b > a:
        return ((b - .50) / .50)
    else:
        return (0)


def show_res(query):
    score = -1 * sent_analyse(query)
    print(score)
    sc = 0
    if score >= 0.8:
        sc = 0.8
    elif score >= 0.6:
        sc = 0.6
    elif score >= 0.4:
        sc = 0.4
    elif score >= 0.2:
        sc = 0.2
    elif score >= 0.0:
        sc = 0.0
    elif score >= -0.2:
        sc = -1 * (-0.2) - 0.2
    elif score >= -0.4:
        sc = -1 * (-0.4)
    elif score >= -0.6:
        sc = -1 * (-0.6) - 0.2
    elif score >= -0.8:
        sc = -1 * (-0.8) - 0.2
    elif score >= -1:
        sc = -1 * (-1) - 0.2
    sc = round(sc, 1)
    d = sorted(data[sc], key=lambda k: data[sc][k])
    selected = []
    arr_len = 10 if 10 < len(d) else len(d)
    for k in range(0, arr_len):
        if data[sc][d[k]] > 0:
            selected.append(d[k])

    for k in selected:
        d.remove(k)
    random.shuffle(d)
    sel_len = len(selected)
    if sel_len < arr_len:
        for k in range(sel_len, arr_len):
            selected.append(d[k])
    return selected, sc


def update_priority(feedback):
    if feedback[2] == 1:
        data[feedback[1]][feedback[0]] += pos
    else:
        data[feedback[1]][feedback[0]] -= neg


# feedback=["Doubtful",-0.6,1]

def create_output_page(arr):

    strTable = "<html><center><table><tr><th>Number<br></th><br><th>Value</th></tr></center>"
    str1 = "<html><head><h1><center><i>Welcome to our predictor!</i><center></h1></head></html>"

    for i in range(len(arr)):
        value = "<tr><td>" + str(i) + "</td><td>" + str(arr[i]) + "</td></tr>"
        strTable = strTable + value

    strTable = strTable + "</table></html>"

    hs = open("C:\\Users\\Admin\\PycharmProjects\\works\\templates\\HTMLTable.html", 'w')

    hs.write(str1)
    hs.write(strTable)
    hs.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getdata',methods=['POST'])
def getdata():
    data = str(request.form['data'])
    l=[data.replace('\n'," ")]
    print(l)
    op, c =show_res(l)
    create_output_page(op)
    return render_template('HTMLTable.html')

@app.route('/changepriority',methods=['POST'])
def changepriority():
    priority=request.form['priority']
    return render_template('random_form.html')
if __name__=="__main__":
    app.run(port=3000)