import flask
from flask import request, jsonify
from flask_cors import CORS
import json
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
#approach1 - using Cosine Similarity
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
import unicodedata
#approach3 - using WordNet
from nltk.corpus import stopwords,wordnet
from itertools import product
import numpy
from urllib.parse import urlparse
import urllib
import re
#FLASK CONFIG
app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app)

import pandas as pd

import numpy as np
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import spacy
import os
from datetime import datetime

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
vocabulary = joblib.load('Features_1.pkl')
Model = joblib.load("CovidModel_1.pkl")
outputFile = 'Output.xlsx'

if not os.path.exists(outputFile):
    dfData = pd.DataFrame({'ID': [],'Ip': [],'Date': [], 'URL': [], 'Title': [] , 'Result': [], 'Highlight': []})
    dfData.to_excel(outputFile, index=False)

def Preprocess(df):
    # remove special characters#
    df = df.replace("[^A-Za-z]+", " ", regex=True).astype(str)
    # remove digits#
    df = df.replace(r'\b\d+\b', ' ', regex=True).astype(str)
    # remove http,https,www digits#
    df = df.replace('https', ' ', regex=True).astype(str)
    df = df.replace('http', ' ', regex=True).astype(str)
    df = df.replace('www', ' ', regex=True).astype(str)
    df = df.replace('com', ' ', regex=True).astype(str)
    # remove single alphabets#
    df = df.replace(r"\b[a-zA-Z]\b", " ", regex=True).astype(str)
    # remove multiple spaces#
    df = df.replace(r'^\s+', '', regex=True).astype(str)
    df = df.replace(' +', ' ', regex=True).astype(str)
    return df

def CheckNewUser(dfUser , ip ):
    idx = dfUser[dfUser['Ip']==ip].index.values
    if len(idx) == 1:
        # print('New user..')
        check = 'new'
    else:
        df = pd.read_excel(outputFile, usecols=['ID', 'Ip', 'Date', 'URL', 'Title', 'Result', 'Highlight'])
        dfG = df.groupby(['Ip'], sort=False)
        g = [dfG.get_group(x) for x in dfG.groups]
        dfData = pd.DataFrame({'ID': [], 'Ip': [], 'Date': [], 'URL': [], 'Title': [], 'Result': [], 'Highlight': []})
        for i in range(len(g)):
            dfg = g[i]
            idx = dfg[dfg['ID'].notnull()].index.tolist()
            if idx == []:
                check = 'new'
                break
            else:
                check = 'old'
                dfg['ID'] = dfg['ID'].fillna(df['ID'].iloc[idx[0]])
                dfData = dfData.append(dfg, ignore_index=True)
                dfData.to_excel(outputFile)
    return check

def CheckNull():
    df = pd.read_excel(outputFile, usecols=['ID','Ip','Date', 'URL', 'Title', 'Result', 'Highlight'] )
    df = df.dropna(subset=['ID'])
    df.to_excel(outputFile)

# def PreprocessDomain(df ):
#     for index, row in df.iterrows():
#         if urlparse(row['source']).netloc:
#             row['domain'] = urlparse(row['source']).netloc
#         else:
#             row['domain'] = row['source']
#     return df['domain']

class stemmer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [token.lemma_ for token in nlp(doc)]   #return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

#HOME
@app.route('/', methods=['GET'])
def home():
    return "<h1>NLP based Analyzer</h1>"


@app.route('/NewUserName', methods=['POST'])
def SaveUser():
    name = unquote(request.json.get('test', ""))
    df = pd.read_excel(outputFile, usecols=['ID','Ip','Date', 'URL', 'Title', 'Result', 'Highlight'] )
    idx = df[df['ID'].isnull()].index.tolist()
    df['ID'].iloc[idx[0]]= name.replace('"', '')
    df.to_excel(outputFile)
    return name


#ANALYZE POST REQ API
@app.route('/analyze', methods=['POST'])
def analyze_context():
    CheckNull()
    article = unquote(request.json.get('article', ""))
    testData = unquote(request.json.get('test_data', ""))
    source_url = unquote(request.json.get('url', ""))
    algo = request.json.get('algo', 'wordnet')
    if not (article and testData):
        return jsonify("Error: missing values")
    #word2vec
    context , highlight, dfList = CheckSimilarity(article=article, testdata=testData, source_url=source_url, algo=algo).relatedContext
    context = context[0].upper()
    print(context)

    # Save id#
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    print( 'ip:',ip)
    # dfUser = pd.read_excel(userFile, usecols=['ID', 'Ip'])
    # Save results#
    dfNew = pd.read_excel(outputFile, usecols=['ID', 'Ip', 'Date', 'URL', 'Title', 'Result', 'Highlight'])
    dfNew = dfNew.append(
        {'ID': '' , 'Ip': ip, 'Date': dfList[0][0], 'URL': dfList[0][1], 'Title': dfList[0][2], 'Result': dfList[0][3], 'Highlight': dfList[0][4]},
        ignore_index=True)
    cols = ['ID','Ip','Date', 'URL','Title', 'Result', 'Highlight']
    dfNew = dfNew[cols]
    dfNew.to_excel(outputFile)
    user = CheckNewUser(dfNew, ip)
    print(user)

    response = {
                    "match":len(highlight)>0,
                    "found":0,
                    "yourSearch":testData,
                    "resp":highlight,
                    "result": context,
                    "user": user
    }
    # print(response)
    return jsonify(response)



#SIMILARITY CHECK
class CheckSimilarity(object):
    def __init__(self, article, testdata, source_url,algo):
        self.article = article
        self.testdata = testdata
        self.source_url = source_url


    @property
    def relatedContext(self):
        # Get the title
        try:
            req = Request(self.source_url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'html.parser')
            title = soup.title.text
            text = ''
            for para in soup.find_all('p'):
                text += (para.text)
        except:
            title = ''
            text = self.article

        title = title
        source = self.source_url
        sente2 = []
        # print('Title...',title)
        # print(text)

        df = pd.DataFrame({'title': [title], 'content': [text], 'publication': [source]})
        df['domain'] = ''
        # lower case#
        df = df.apply(lambda x: x.astype(str).str.lower())
        # text#
        Pre_text = Preprocess(df['content'])
        # title#
        Pre_title = Preprocess(df['title'])
        # source#
        # Pre_source = PreprocessDomain(df)
        # Pre_url = Preprocess(Pre_source)
        # print(Pre_url)
        #Data#
        data =  Pre_text + Pre_title #+ Pre_url
        #Filter corpus#
        dictionary = ['covid' , 'corona', 'coronavirus' ]#, '-cov-2','cov2','ncov'
        filter = Pre_text.apply(lambda x: any([k in x for k in dictionary]))

        if filter.any():
            FullData_S = data.to_string(header=False, index=False)
            if not FullData_S:
                r = "Please enter data"
            else:
                vectorizer = TfidfVectorizer(tokenizer=stemmer(), stop_words='english', max_df=0.8,ngram_range=(1,2),
                                             vocabulary=vocabulary) #ngram_range=(2,2)
                feature = vectorizer.fit_transform(data)
                result = Model.predict(feature)
                # print('******* Highlighting *********')
                if result[0] == 'fake':
                    Mc = feature.tocoo()
                    di = {k: v for k, v in zip(Mc.col, Mc.data)}
                    sorted_di = dict(sorted(di.items(), key=lambda item: item[1], reverse=True)[:5]) #[:10]
                    values = []
                    for i in sorted_di:
                        values.append(vectorizer.get_feature_names()[i])
                    # print(values)
                    sente = []
                    for i in range(0, len(values)):
                        for sentence in text.split('.'):
                            st = sentence.lower()
                            if st.find(values[i].split(' ')[0]) >= 0:
                                if sentence.strip() not in sente2:
                                    st = re.split(r"[^a-zA-Z0-9\s]", sentence.strip())
                                    sente2.append(sentence.strip())
                                    for elem in st:
                                        if not elem.strip():
                                            st.remove(elem)
                                    sente.append(st[0])
                                    break
                    for i in sente:
                        print('Answer......', i + '\n')
                    related_context = []
                    for i in sente:
                        related_context.append({"sentence": unicodedata.normalize('NFKD', i), "similarityIndex": 0.96})
                else:
                    related_context =[]
        else:
            result = ['none']
            related_context = []
        # Save
        dfList = []
        dfList.append([datetime.now(),source,title,result[0].upper(),sente2 ])
        # dfNew.to_excel(outputFile)

        return result, related_context, dfList

#APP RUNSERVER
if __name__ == "__main__":
#APP RUNSERVER
    #app.run(debug=True, use_reloader=False)
    app.run()
