import json,time
import os.path
import jieba,re
import datetime
import hashlib
from libs.Utils import Utils
from libs.Crawler_and_Share.load_data_from_mysql import load_data_from_mysql


class PostData():
    def __init__(self):
        self.post_data = load_data_from_mysql(data_name = 'Stock')
        print("Get data from DB done")
        
    def get_emotion_dict(self, path = "chinese-corpus/emotion-dic/taiwan/", dict_list = ['NTUSD_positive_simplified.txt','NTUSD_negative_simplified.txt']):
        #load emotion dict
        def get_emotion_dict_from_file(path, emotion_score): 
            emotion_dict = {} 
            with open(path, 'r') as f: 
                for line in f: 
                    key = line.strip()
                    emotion_dict[key] = int(emotion_score) 
            return emotion_dict
    
        emotion_dict = {}
        for dl in dict_list:
            #using file name to check the file is positive dictionary or negative dictionary
            emo_score = 1 if 'positive' in dl.lower() else -1
            #combine with exist emotion dictionary
            emotion_dict={**emotion_dict, **get_emotion_dict_from_file(path + dl, emo_score)}
        return emotion_dict
    
    def calc_emotion_score(self, seg_list, emotion_dict):
        news_positive_score=0
        news_negative_score=0
        for word in seg_list:
            if word in emotion_dict:
                if emotion_dict[word] < 0:
                    news_negative_score += abs(emotion_dict[word])
                else:
                    news_positive_score += emotion_dict[word]
        return news_positive_score, news_negative_score

    def custom_clean_article(self ,article):
        article = re.sub('[\d]', '', article)
        article = re.sub('[\n]', '', article)
        return article
    
    def seg_article(self, article):
        return list(filter(None, jieba.cut(article, cut_all=True)))
    
    def make_post_data(self, json_file_path = "newsJSONData.json"):
        json_data = {"parsedMD5":[], "dayScore":{}, "startDate": time.strftime("%Y-%m-%d")}
        for post in self.post_data.iterrows():
            #calculate MD5 of article
            article_MD5 = hashlib.md5(post[1]['clean_article'].encode('utf-8')).hexdigest()
            #if the article have been parsed before, there's no need to parse again
            if article_MD5 not in json_data["parsedMD5"]:
                #get the date of the article
                article_date = post[1]['date']
                #change the date to regular format, EX:date format:2007-07-24 13:10:49 to 2007-07-24
                article_date_format = datetime.datetime.strptime(article_date, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                #if the date is before 1911-01-01 ,means incorrect date
                if article_date_format < datetime.datetime.strptime('1911-01-01', '%Y-%m-%d').strftime("%Y-%m-%d"):
                    continue
                #update the oldest date
                if article_date_format < json_data["startDate"]:
                    json_data["startDate"] = article_date_format
                article_date = str(article_date_format)
                #if json do not contains the day's score, initialize day score
                if article_date not in json_data["dayScore"]:
                    json_data["dayScore"][article_date] = [0, 0]
                #use the value of clean_article as article
                article = post[1]['clean_article']
                #using custom cleaner to clean the data 
                article = self.custom_clean_article(article)
                #segment the article
                seg_list = self.seg_article(article)
                #get emotion dictionary
                emotion_dict = self.get_emotion_dict()
                #calculate the emotion score
                news_positive_score, news_negative_score = self.calc_emotion_score(seg_list, emotion_dict)
                #add positive score
                json_data["dayScore"][article_date][0] += news_positive_score
                #add negative score
                json_data["dayScore"][article_date][1] += news_negative_score
                #add MD5 to list for record the document have been parsed before 
                json_data["parsedMD5"].append(article_MD5)
        #write to json file
        Utils.write_json_to_file(json_data, json_file_path)
        print("The file have been made at " + json_file_path)