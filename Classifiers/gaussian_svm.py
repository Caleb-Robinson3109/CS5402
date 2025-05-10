import pandas as pd
import numpy as np
from sklearn.svm import SVC
from smote_variants import A_SUWO
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

    model = SVC(kernel='rbf', gamma='scale', probability=True)  # Gaussian SVM (RBF kernel)
    model.fit(trainX, trainY)

    y_pred = model.predict(testX)

    #y_pred = ""
    dataIterator.storePredictions(testY, y_pred)
    print("Finished Iteration")

dataIterator.calculateMetrics()
