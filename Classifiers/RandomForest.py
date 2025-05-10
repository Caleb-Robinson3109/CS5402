import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, balanced_accuracy_score, precision_recall_curve, roc_curve, matthews_corrcoef
from sklearn.utils.class_weight import compute_class_weight
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from smote_variants import A_SUWO
from imblearn.metrics import specificity_score
import matplotlib.pyplot as plt
import CrossValidation

#get our kfoldcv iterator
dataIterator = iter(CrossValidation.KFoldCV(10))

for p in dataIterator:
    if type(StopIteration) == type(p):
        break
    trainX, trainY, testX, testY = p

    print("Started Iteration")
    #standardize predictors
    maxes = [] #keep track of mins and maxes so we can modify our test set data
    mins = []
    for col in range(trainX.shape[1]):
        mins.append(min(trainX[:, col]))
        maxes.append(max(trainX[:, col]))
        trainX[:, col] = (trainX[:, col] - mins[col]) / (maxes[col] - mins[col]) 
        testX[:, col] = (testX[:, col] - mins[col]) / (maxes[col] - mins[col]) 

    #Apply A_SUWO oversampling to the training set to handle imbalanced data
    trainX, trainY = A_SUWO().sample(trainX, trainY)

    #build and fit Decision tree classifier
    clf = RandomForestClassifier(n_estimators = 10000, criterion='entropy', random_state=1)
    clf.fit(trainX, trainY)

    dataIterator.storePredictions(testY, clf.predict(testX))
    print("Finished Iteration")

dataIterator.calculateMetrics()
