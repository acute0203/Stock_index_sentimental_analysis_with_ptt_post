from libs.ClassificationModel import ClassificationModel
from sklearn.naive_bayes import GaussianNB

class GaussianNaiveBayesClassification(ClassificationModel):
    def __init__(self):
        self.model = GaussianNB()
        
    def train(self,training_data, training_labels):
        self.model.fit(training_data, training_labels)
    
    def predict(self, predict_data):
        return self.model.predict(predict_data)
    