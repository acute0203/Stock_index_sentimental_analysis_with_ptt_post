from datetime import datetime,timedelta
from sklearn.cluster import KMeans
import numpy as np
import os,json,time
import datetime as dt
import os.path
from libs.GaussianNaiveBayesClassification import GaussianNaiveBayesClassification
from libs.PostData import PostData
from libs.PriceData import PriceData
from libs.Utils import Utils

def normalize_emotion_score(emotion_score_list):
    total_score=sum(emotion_score_list) + 1
    return [float(score) / total_score for score in emotion_score_list]

def pare_training_data(date_price, date_article_score):
    training_index=[]
    training_emotion=[]
    for date in date_article_score:
        date_format=datetime.strptime(date, "%Y-%m-%d")
        #add one day
        next_day=str((date_format + timedelta(days = 1)).strftime("%Y-%m-%d"))
        if (next_day in date_price) and (normalize_emotion_score(date_article_score[date])!=0):
            training_index.append([date_price[next_day]])
            training_emotion.append(normalize_emotion_score(date_article_score[date]))
    return training_index,training_emotion

#clustering the stock price with n cluster, where n is cluster number
def price_clustering(training_index, n = 10):
    X = np.array(training_index)
    kmeans = KMeans(n_clusters=n, random_state=0).fit(X)
    clustering_result = kmeans.labels_
    clustering_center = kmeans.cluster_centers_
    return np.array(clustering_result), clustering_center

def main():
    #read date score from json
    json_file_path = "newsJSONData.json"
    #if the file does not exist, then it will load the data from database, which was provided by
    #https://github.com/jwlin/ptt-web-crawler
    if not os.path.exists(json_file_path):
        pdata = PostData()
        pdata.make_post_data(json_file_path)
    json_data = Utils.read_json_from_file(json_file_path)
    #initial date we need to fetch 
    start_date = json_data['startDate']
    date_article_score = json_data['dayScore']
    #EX : date_article_score={"2016-12-05":[4,3],"2016-12-06":[1,1],"2016-12-07":[3,10],"2016-12-08":[3,9]}
    #set end date at 2018-02-07
    end_date = datetime.strptime('2018-02-07', '%Y-%m-%d').strftime("%Y-%m-%d")
    print("Article start date:" + str(start_date))
    print("Set up analyze end date:" + str(end_date))
    #init data
    data = PriceData(start_date, end_date, company = "TSM",source = 'google')
    #get date price 
    date_price = data.get_price_data()
    #combine date price and date score
    training_index, training_emotion = pare_training_data(date_price, date_article_score)
    #clustering the price into n group, where n by default is set to 10. 
    #it will retuurn the clustering result of each data and the center of each group
    clustering_result, clustering_center= price_clustering(training_index, n = 10)

    #classification
    #initialize
    cm = GaussianNaiveBayesClassification()
    #Using clustering result to train classification model.
    cm.train(training_emotion, clustering_result)

    #using the end date to test it can work or not
    end_date = str(end_date)
    if end_date in date_article_score and (normalize_emotion_score(date_article_score[end_date])!=0):
        today_emotion_score = normalize_emotion_score(date_article_score[end_date])
        #working correct
        print("Index close price might close to "+str(clustering_center[cm.predict(np.array([today_emotion_score]))]))
    else:
        #working wrong
        print("Something Wrong...")
        print(date_article_score)
        print()

if __name__ == "__main__":
    main()