import nltk
import re
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from flair.models import TextClassifier
from flair.data import Sentence
#라이브러리 선언부

stop_words = stopwords.words('english')
stemmer = PorterStemmer()
tweet_tokenizer = TweetTokenizer()

class sentimental_analysis:
    #데이터프레임을 입력받아 클래스초기화
    def __init__(self,twitter_data):
        self.twitter_data = twitter_data
        self.twitter_data['clean_text'] = np.NaN
        self.twitter_data['vader'] = np.NaN
        self.twitter_data['textblob'] = np.NaN
    #vader,textblob,flair 옵션 입력
    def process(self,option):        
        #데이터 프레임 전처리 텍스트
        self.twitter_data = self.twitter_data.drop(self.twitter_data.columns[[0,1,2,3,4,5,6,7,10,11,12]],axis=1)
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        clean_tweet = []
        tweet = self.twitter_data
        if option == 'textblob':
            for index,row in tweet.iterrows():
                tweet_list_corpus = re.sub(korean, '', row['text'])
                # URL 제거
                clear_text = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",repl= ' ', string = tweet_list_corpus) # http로 시작되는 url
                clear_text = clear_text.replace('\n',' ').replace('\t',' ')
                clear_text = re.sub('RT @[\w_]+: ',' ', clear_text)
                # Hashtag 제거
                clear_text = re.sub('[#]+[0-9a-zA-Z_]+', ' ', clear_text)
                clear_text = clear_text.lower()
                word_list = tweet_tokenizer.tokenize(clear_text)
                word_list = [word for word in word_list if word not in stop_words]
                word_list = [stemmer.stem(word) for word in word_list]
                text = ' '.join(word_list)
                self.twitter_data.loc[index,'clean_text'] = text
        elif option == 'vader' or option =='flair':
            for index,row in tweet.iterrows():
                tweet_list_corpus = re.sub(korean, '', row['text'])
                clear_text = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",repl= ' ', string = tweet_list_corpus) # http로 시작되는 url
                clear_text = clear_text.replace('\n',' ').replace('\t',' ')
                clear_text = re.sub('RT @[\w_]+: ',' ', clear_text)
                # Hashtag 제거
                clear_text = re.sub('[#]+[0-9a-zA-Z_]+', ' ', clear_text)
                word_list = tweet_tokenizer.tokenize(clear_text)
                word_list = [word for word in word_list if word not in stop_words]
                word_list = [stemmer.stem(word) for word in word_list]
                text = ' '.join(word_list)
                self.twitter_data.loc[index,'clean_text'] = text
        
    def sentimental_vader(self):                    
        result_tweet = self.twitter_data
        #전처리된 csv파일 다시 reload
        text_list = list(result_tweet['clean_text'])
        senti_analyzer = SentimentIntensityAnalyzer()
        twitter_vader_score = []
        for i in range(0,len(text_list)):
            test = str(text_list[i])
            senti_scores = senti_analyzer.polarity_scores(test)
            twitter_vader_score.append(senti_scores['compound'])
        #감정 분석 부분 
        for i in range(len(result_tweet)):
            self.twitter_data.loc[i,'vader'] = twitter_vader_score[i]
        #감정 분석 점수 데이터프레임에 추가
    
    #플레어 감정분석기
    def sentimental_flair(self,file_name):
        result_tweet = self.twitter_data
        text_list = list(result_tweet['clean_tweet'])
        senti_analyzer = TextClassifier.load('en-sentiment')
        twitter_flair_score = []
        for i in range(0,len(text_list)):
            sentence = Sentence(text_list[i])
            senti_analyzer.predict(sentence,return_probabilities_for_all_classes=True)
            if sentence.labels[0].score > sentence.labels[1].score:
                twitter_flair_score.append(sentence.labels[0].score)
            else:
                twitter_flair_score.append((sentence.labels[1].score)*(-1))
        for i in range(0,len(result_tweet)):
            self.twitter_data.loc[i,'flair'] = twitter_flair_score[i]     
    #감정분석 완료 이후 save함수를 통해서 데이터프레임 csv로 저장
    def save_csv(self):
        self.twitter_data.to_csv('senti_tweet',mode = 'w')        
            #sentence 클래스 학습 이후 점수만 추출 예정