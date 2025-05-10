import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, balanced_accuracy_score, precision_recall_curve, roc_curve, matthews_corrcoef, precision_score, recall_score
from imblearn.metrics import specificity_score


class KFoldCV():
    def __init__(self, k):
        self.k = k
        self.predictions = []
        self.yVals = []
        self.inputSize = 0

    def __iter__(self):
        self.df = pd.read_csv("CompiledDataFix.csv").sample(frac=1) #shuffle rows on entry
        self.inputSize = self.df.shape[0]
        self.x = self.df.iloc[:, 2:].values.astype('float32') 
        self.y = (self.df.iloc[:, 1].values.astype('int32') * 2 - 1) #map labels to -1 or 1 instead of 0 or 1
        self.x = self.x[:, :-2] #temporarily remove last two rows because they are not currently populated
        self.current = 0
        self.testSize = int(self.x.shape[0] / self.k)
        return self
    
    def __next__(self):
        if self.current + self.testSize > self.x.shape[0]:
            return StopIteration
        testX = self.x[self.current:self.current+self.testSize]
        testY = self.y[self.current:self.current+self.testSize]
        trainX = np.concatenate([self.x[0:self.current], self.x[self.current+self.testSize:]])
        trainY = np.concatenate([self.y[0:self.current], self.y[self.current+self.testSize:]])

        self.current += self.testSize
        print(len(testX), len(testY), len(trainX), len(trainY))
        return (trainX, trainY, testX, testY)
    
    def storePredictions(self, test_y, pred_y):
        self.yVals += list(test_y)
        self.predictions += list(pred_y)

    def calculateMetrics(self):
        assert len(self.yVals) == self.inputSize - (self.inputSize % self.k)
        assert len(self.predictions) == self.inputSize - (self.inputSize % self.k)
        print(f'Accuracy: {accuracy_score(self.yVals, self.predictions)}')
        print(f'F1 Score: {f1_score(self.yVals, self.predictions)}')
        print(f'Precision: {precision_score(self.yVals, self.predictions)}')
        print(f'Recall: {recall_score(self.yVals, self.predictions)}')
        print(f"Balanced Accuracy: {balanced_accuracy_score(self.yVals, self.predictions)}")
        print(f"matthews_corrcoef: {matthews_corrcoef(self.yVals, self.predictions)}")
        print(f"Specificity: {specificity_score(self.yVals, self.predictions)}")
        confMatrix = confusion_matrix(self.yVals, self.predictions)
        labeledMatrix = pd.DataFrame(confMatrix, index=['True Neg', 'True Pos'], columns=['Pred Neg', 'Pred Pos'])
        print(labeledMatrix)
